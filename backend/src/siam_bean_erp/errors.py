from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

LABELS = {
    "email": "Email",
    "full_name": "Name",
    "role": "Role",
    "password": "Password",
    "sku": "SKU",
    "name": "Name",
    "unit": "Unit",
    "cost": "Cost",
    "price": "Price",
    "reorder_level": "Reorder level",
    "tax_id": "Tax ID",
    "payment_terms": "Payment terms",
    "quantity": "Quantity",
    "product_id": "Product",
    "customer_id": "Customer",
    "amount": "Amount",
    "reason": "Reason",
    "lines": "Order lines",
}


def label(field: object) -> str:
    return LABELS.get(str(field), str(field).replace("_", " ").capitalize())


def humanize(error: dict) -> str:
    field = error["loc"][-1] if error["loc"] else "Request"
    kind = error["type"]
    if kind == "missing":
        return f"{label(field)} is required"
    if kind == "literal_error":
        options = error.get("ctx", {}).get("expected", "").replace("'", "").replace(" or ", ", ")
        return f"{label(field)} must be one of: {options}"
    if kind == "value_error":
        return str(error["msg"]).removeprefix("Value error, ")
    if kind in ("int_parsing", "int_from_float", "decimal_parsing", "decimal_type", "float_parsing"):
        return f"{label(field)} must be a number"
    if kind in ("string_type", "string_too_short"):
        return f"{label(field)} is required"
    return f"{label(field)}: {error['msg']}"


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": humanize(exc.errors()[0])})
