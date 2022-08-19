from typing import List, Optional

from pydantic import BaseModel


class SolendAsset(BaseModel):
    name: str
    symbol: str
    decimals: int
    mintAddress: str


class SolendReserve(BaseModel):
    asset: str
    address: str
    collateralMintAddress: str
    collateralSupplyAddress: str
    liquidityAddress: str
    liquidityFeeReceiverAddress: str


class SolendMarket(BaseModel):
    name: str
    isPrimary: bool
    description: Optional[str]
    creator: str
    address: str
    authorityAddress: str
    reserves: List[SolendReserve]


class OracleAsset(BaseModel):
    asset: str
    priceAddress: str
    switchboardFeedAddress: str


class SolendOracle(BaseModel):
    pythProgramID: str
    switchboardProgramID: str
    assets: List[OracleAsset]


class ISolendMarketReserve(BaseModel):
    programID: str
    assets: List[SolendAsset]
    markets: List[SolendMarket]
    oracles: SolendOracle
