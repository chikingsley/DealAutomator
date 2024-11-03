from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY, Boolean, DECIMAL
from sqlalchemy.sql import func
from app.db.base import Base

class MessageProcessing(Base):
    __tablename__ = "message_processing"

    id = Column(Integer, primary_key=True)
    telegram_message_id = Column(String)
    raw_text = Column(Text)
    status = Column(String(20))  # 'pending', 'processing', 'completed', 'failed'
    attempts = Column(Integer, default=0)
    partner_name = Column(String)
    processed_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class ParsedDeal(Base):
    __tablename__ = "parsed_deals"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('message_processing.id'))
    geo = Column(String(2))
    language_code = Column(String(5))
    is_native = Column(Boolean)
    pricing_model = Column(String(3))  # 'CPA' or 'CPL'
    cpa_amount = Column(DECIMAL)
    crg_percentage = Column(DECIMAL)
    cpl_amount = Column(DECIMAL)
    deduction_limit = Column(Text)
    conversion_rate = Column(Text)
    conversion_current = Column(Text)
    conversion_details = Column(Text)
    sources = Column(ARRAY(String))
    funnels = Column(ARRAY(String))
    notion_url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
