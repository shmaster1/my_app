from pydantic import BaseModel


#  Represents individual items within an order
class OrderItem(BaseModel):
      item_id: int  # Link to the product
      item_name: str
      price: float
      quantity: int