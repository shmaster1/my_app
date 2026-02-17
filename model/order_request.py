from pydantic import BaseModel


# Data sent by the user to modify or finalize an order
class OrderRequest(BaseModel):
  item_id:  int       # Required for add/remove item flow
  quantity: int  # Used to update stock quantities upon purchase
  shipping_address: str  # Required to finalize the order


