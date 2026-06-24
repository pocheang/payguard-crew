"""
完整的 KYC (Know Your Customer) 验证流程
包括身份验证、地址验证、文件验证等
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class KYCLevel(str, Enum):
    """KYC 认证等级"""
    UNVERIFIED = "unverified"  # 未认证
    BASIC = "basic_verified"  # 基础认证（手机号）
    STANDARD = "standard_verified"  # 标准认证（身份证）
    ENHANCED = "enhanced_verified"  # 增强认证（人脸识别）
    FULL = "full_verified"  # 完整认证（地址证明）


class DocumentType(str, Enum):
    """文档类型"""
    ID_CARD = "id_card"  # 身份证
    PASSPORT = "passport"  # 护照
    DRIVING_LICENSE = "driving_license"  # 驾驶证
    UTILITY_BILL = "utility_bill"  # 水电账单
    BANK_STATEMENT = "bank_statement"  # 银行对账单
    PROOF_OF_ADDRESS = "proof_of_address"  # 地址证明


class KYCDocument(BaseModel):
    """KYC 文档"""
    document_type: DocumentType
    document_number: str
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    verified: bool = False
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None


class KYCProfile(BaseModel):
    """KYC 用户档案"""
    user_id: str
    kyc_level: KYCLevel = KYCLevel.UNVERIFIED

    # 基础信息
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None

    # 联系信息
    phone_number: Optional[str] = None
    phone_verified: bool = False
    email: Optional[str] = None
    email_verified: bool = False

    # 地址信息
    residential_address: Optional[str] = None
    address_verified: bool = False

    # 文档列表
    documents: List[KYCDocument] = Field(default_factory=list)

    # 生物识别
    face_verified: bool = False
    face_verified_at: Optional[datetime] = None

    # 审核信息
    risk_score: int = 0  # 0-100
    risk_level: str = "unknown"  # low, medium, high

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed_at: Optional[datetime] = None

    # 审核状态
    review_status: str = "pending"  # pending, approved, rejected, suspended
    review_notes: Optional[str] = None
    reviewed_by: Optional[str] = None


class KYCVerificationRequest(BaseModel):
    """KYC 验证请求"""
    user_id: str
    verification_type: str  # phone, email, id_card, face, address
    data: Dict  # 验证数据


class KYCVerificationResult(BaseModel):
    """KYC 验证结果"""
    success: bool
    kyc_level: KYCLevel
    message: str
    details: Optional[Dict] = None
    next_steps: Optional[List[str]] = None


class KYCService:
    """KYC 服务"""

    def __init__(self, db_repository):
        self.db = db_repository

    async def create_kyc_profile(self, user_id: str) -> KYCProfile:
        """创建 KYC 档案"""
        profile = KYCProfile(user_id=user_id)
        await self.db.save_kyc_profile(profile)
        return profile

    async def get_kyc_profile(self, user_id: str) -> Optional[KYCProfile]:
        """获取 KYC 档案"""
        return await self.db.get_kyc_profile(user_id)

    async def verify_phone(self, user_id: str, phone_number: str, code: str) -> KYCVerificationResult:
        """验证手机号"""
        profile = await self.get_kyc_profile(user_id)
        if not profile:
            profile = await self.create_kyc_profile(user_id)

        # TODO: 实际验证短信验证码
        is_valid = self._verify_sms_code(phone_number, code)

        if is_valid:
            profile.phone_number = phone_number
            profile.phone_verified = True
            profile.kyc_level = KYCLevel.BASIC
            profile.updated_at = datetime.utcnow()
            await self.db.update_kyc_profile(profile)

            return KYCVerificationResult(
                success=True,
                kyc_level=KYCLevel.BASIC,
                message="手机号验证成功",
                next_steps=["请上传身份证进行标准认证"]
            )

        return KYCVerificationResult(
            success=False,
            kyc_level=profile.kyc_level,
            message="验证码错误"
        )

    async def verify_identity_document(
        self,
        user_id: str,
        document_type: DocumentType,
        document_number: str,
        document_data: Dict
    ) -> KYCVerificationResult:
        """验证身份证件"""
        profile = await self.get_kyc_profile(user_id)
        if not profile:
            return KYCVerificationResult(
                success=False,
                kyc_level=KYCLevel.UNVERIFIED,
                message="请先完成手机号验证"
            )

        # OCR 识别和验证
        is_valid, extracted_data = self._verify_document_ocr(document_type, document_data)

        if is_valid:
            document = KYCDocument(
                document_type=document_type,
                document_number=document_number,
                verified=True,
                verified_at=datetime.utcnow()
            )
            profile.documents.append(document)
            profile.full_name = extracted_data.get("name")
            profile.date_of_birth = extracted_data.get("date_of_birth")
            profile.kyc_level = KYCLevel.STANDARD
            profile.updated_at = datetime.utcnow()
            await self.db.update_kyc_profile(profile)

            return KYCVerificationResult(
                success=True,
                kyc_level=KYCLevel.STANDARD,
                message="身份证件验证成功",
                details=extracted_data,
                next_steps=["请进行人脸识别认证"]
            )

        return KYCVerificationResult(
            success=False,
            kyc_level=profile.kyc_level,
            message="身份证件验证失败"
        )

    async def verify_face(self, user_id: str, face_data: Dict) -> KYCVerificationResult:
        """人脸识别验证"""
        profile = await self.get_kyc_profile(user_id)
        if not profile or profile.kyc_level not in [KYCLevel.STANDARD, KYCLevel.ENHANCED, KYCLevel.FULL]:
            return KYCVerificationResult(
                success=False,
                kyc_level=profile.kyc_level if profile else KYCLevel.UNVERIFIED,
                message="请先完成身份证件验证"
            )

        # 人脸识别和活体检测
        is_valid, similarity = self._verify_face_recognition(face_data)

        if is_valid and similarity > 0.85:
            profile.face_verified = True
            profile.face_verified_at = datetime.utcnow()
            profile.kyc_level = KYCLevel.ENHANCED
            profile.updated_at = datetime.utcnow()
            await self.db.update_kyc_profile(profile)

            return KYCVerificationResult(
                success=True,
                kyc_level=KYCLevel.ENHANCED,
                message="人脸识别验证成功",
                details={"similarity": similarity},
                next_steps=["请上传地址证明完成完整认证"]
            )

        return KYCVerificationResult(
            success=False,
            kyc_level=profile.kyc_level,
            message="人脸识别验证失败"
        )

    async def verify_address(self, user_id: str, address: str, proof_document: Dict) -> KYCVerificationResult:
        """验证地址"""
        profile = await self.get_kyc_profile(user_id)
        if not profile or profile.kyc_level != KYCLevel.ENHANCED:
            return KYCVerificationResult(
                success=False,
                kyc_level=profile.kyc_level if profile else KYCLevel.UNVERIFIED,
                message="请先完成人脸识别验证"
            )

        # 验证地址证明文件（水电账单、银行对账单等）
        is_valid = self._verify_address_proof(proof_document)

        if is_valid:
            document = KYCDocument(
                document_type=DocumentType.PROOF_OF_ADDRESS,
                document_number="",
                verified=True,
                verified_at=datetime.utcnow()
            )
            profile.documents.append(document)
            profile.residential_address = address
            profile.address_verified = True
            profile.kyc_level = KYCLevel.FULL
            profile.review_status = "approved"
            profile.updated_at = datetime.utcnow()
            await self.db.update_kyc_profile(profile)

            return KYCVerificationResult(
                success=True,
                kyc_level=KYCLevel.FULL,
                message="地址验证成功，KYC 认证已完成",
                next_steps=["您已完成完整 KYC 认证"]
            )

        return KYCVerificationResult(
            success=False,
            kyc_level=profile.kyc_level,
            message="地址证明验证失败"
        )

    async def assess_kyc_risk(self, user_id: str) -> Dict:
        """评估 KYC 风险"""
        profile = await self.get_kyc_profile(user_id)
        if not profile:
            return {"risk_score": 100, "risk_level": "high", "reasons": ["未完成 KYC 认证"]}

        risk_score = 0
        reasons = []

        # 根据 KYC 等级评分
        if profile.kyc_level == KYCLevel.UNVERIFIED:
            risk_score += 50
            reasons.append("未完成任何 KYC 认证")
        elif profile.kyc_level == KYCLevel.BASIC:
            risk_score += 30
            reasons.append("仅完成基础认证")
        elif profile.kyc_level == KYCLevel.STANDARD:
            risk_score += 15
            reasons.append("未完成人脸识别")
        elif profile.kyc_level == KYCLevel.ENHANCED:
            risk_score += 5
            reasons.append("未完成地址验证")

        # 文档有效期检查
        for doc in profile.documents:
            if doc.expiry_date and doc.expiry_date < datetime.utcnow():
                risk_score += 20
                reasons.append(f"{doc.document_type} 已过期")

        # 更新时间检查
        if profile.updated_at < datetime.utcnow() - timedelta(days=365):
            risk_score += 10
            reasons.append("KYC 信息超过一年未更新")

        # 确定风险等级
        if risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 20:
            risk_level = "medium"
        else:
            risk_level = "low"

        profile.risk_score = risk_score
        profile.risk_level = risk_level
        await self.db.update_kyc_profile(profile)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "reasons": reasons
        }

    # 私有辅助方法（实际实现需要接入第三方服务）

    def _verify_sms_code(self, phone_number: str, code: str) -> bool:
        """验证短信验证码（模拟实现）"""
        # TODO: 接入短信服务商 API
        return len(code) == 6 and code.isdigit()

    def _verify_document_ocr(self, document_type: DocumentType, document_data: Dict) -> tuple[bool, Dict]:
        """OCR 识别和验证证件（模拟实现）"""
        # TODO: 接入 OCR 服务
        return True, {
            "name": "示例姓名",
            "date_of_birth": datetime(1990, 1, 1),
            "id_number": "110101199001011234"
        }

    def _verify_face_recognition(self, face_data: Dict) -> tuple[bool, float]:
        """人脸识别和活体检测（模拟实现）"""
        # TODO: 接入人脸识别服务
        return True, 0.95

    def _verify_address_proof(self, proof_document: Dict) -> bool:
        """验证地址证明文件（模拟实现）"""
        # TODO: 接入文档验证服务
        return True
