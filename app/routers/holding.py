from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.models.schemas.holding_schema import (
    HoldingCreateSchema,
    HoldingDisplaySchema,
    HoldingUpdateSchema,
    HoldingDetailDisplaySchema,
)
from app.models.database import holding_db
from utils.db_connection_manager import get_db
from utils.auth import get_current_user
from app.models.schemas.user_schema import UserBaseSchema

router = APIRouter(prefix="/holdings", tags=["holdings"])


@router.get(
    "/scan/{scan_id}",
    response_model=List[HoldingDisplaySchema],
    summary="Get holdings by scan ID",
    description="Retrieve a list of holdings for a given scan ID.",
)
def get_holdings_by_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: UserBaseSchema = Depends(get_current_user),
):
    return holding_db.get_holdings_by_scan(db, scan_id, current_user)


@router.get(
    "/prospect/{prospect_id}",
    response_model=List[HoldingDisplaySchema],
    summary="Get holdings by prospect ID",
    description="Retrieve a list of holdings for a given prospect ID.",
)
def get_holdings_by_prospect(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: UserBaseSchema = Depends(get_current_user),
):
    return holding_db.get_holdings_by_prospect(db, prospect_id, current_user)


@router.post(
    "/",
    response_model=HoldingDetailDisplaySchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new holding",
    description="Create a new holding. Only the advisor of the prospect can create holdings.",
)
def create_holding(
    holding: HoldingCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserBaseSchema = Depends(get_current_user),
):
    return holding_db.create_holding(db, holding, current_user)


@router.get(
    "/{holding_id}",
    response_model=HoldingDetailDisplaySchema,
    summary="Get a specific holding",
    description="Retrieve a specific holding by its ID.",
)
def get_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: UserBaseSchema = Depends(get_current_user),
):
    return holding_db.get_holding_by_id(db, holding_id, current_user)


@router.put(
    "/{holding_id}",
    response_model=HoldingDetailDisplaySchema,
    summary="Update a holding",
    description="Update an existing holding. Only the advisor of the prospect can update holdings.",
)
def update_holding(
    holding_id: int,
    holding: HoldingUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserBaseSchema = Depends(get_current_user),
):
    return holding_db.update_holding(db, holding_id, holding, current_user)


@router.delete(
    "/{holding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a holding",
    description="Delete a holding by its ID. Only the advisor of the prospect can delete holdings.",
)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: UserBaseSchema = Depends(get_current_user),
):
    holding_db.delete_holding(db, holding_id, current_user)
