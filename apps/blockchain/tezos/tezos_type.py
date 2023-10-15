from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ITezosAccountTxn(BaseModel):
    id: int
    hash: str
    type: str
    block: str
    time: datetime
    height: int
    cycle: int
    counter: int
    op_n: int
    op_p: int
    status: str
    is_success: bool
    gas_limit: int
    gas_used: int
    storage_limit: int
    volume: float
    fee: float
    burned: Optional[float] = None
    sender: str
    receiver: str
    confirmations: int
