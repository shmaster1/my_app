from model.ecom.customer_order import CustomerOrder
from model.ecom.customer_order_request import CustomerOrderRequest
from model.ecom.customer_order_response import CustomerOrderResponse
from repository.ecom import customer_order_repository
from service.ecom import customer_service


async def get_customer_order_by_id(customer_order_id: int):
    return await customer_order_repository.get_by_id(customer_order_id)


async def create_customer_order(customer_order_request: CustomerOrderRequest) -> CustomerOrderResponse:
    selected_customer = customer_order_request.customer # whats coming from the req

    if selected_customer.id is None:
        created_customer_id = await customer_service.create_customer(selected_customer)
        selected_customer = await customer_service.get_customer_by_id(created_customer_id) # better to have different name like db_customer for ex
        customer_order_request.customer_order.customer_id = created_customer_id

    else:
        existing_customer = customer_service.get_customer_by_id(selected_customer.id)
        if existing_customer is None:
            raise Exception(f"Can't find existing customer with id {selected_customer.id}")

    customer_order_request.customer = selected_customer
    customer_order = customer_order_request.customer_order

    await customer_order_repository.create_customer_order(customer_order)

    customer_orders = await customer_order_repository.get_by_customer_id(selected_customer.id)
    return CustomerOrderResponse(customer=selected_customer, customer_orders=customer_orders)


async def update_customer_order(customer_order_id: int, customer_order: CustomerOrder):
    await customer_order_repository.update_customer_order(customer_order_id, customer_order)


async def delete_customer_order(customer_order_id: int):
    await customer_order_repository.delete_customer_order(customer_order_id)