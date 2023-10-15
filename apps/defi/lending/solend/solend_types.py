from typing import Optional

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
    description: Optional[str] = None
    creator: str
    address: str
    authorityAddress: str
    reserves: list[SolendReserve]


class OracleAsset(BaseModel):
    asset: str
    priceAddress: str
    switchboardFeedAddress: str


class SolendOracle(BaseModel):
    pythProgramID: str
    switchboardProgramID: str
    assets: list[OracleAsset]


class ISolendMarketReserve(BaseModel):
    programID: str
    assets: list[SolendAsset]
    markets: list[SolendMarket]
    oracles: SolendOracle
