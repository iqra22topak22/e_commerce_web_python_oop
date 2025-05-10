
# ============================
import streamlit as st
from abc import ABC, abstractmethod
import uuid
import re

# Define the classes (Entities and Payments)
class Entity:
    def __init__(self, entity_id, name):
        self.entity_id = entity_id
        self.name = name

class Product(Entity):
    def __init__(self, product_id, name, description, price, stock):
        super().__init__(product_id, name)
        self.description = description
        self._price = price
        self._stock = stock

    def update_stock(self, quantity):
        if quantity <= self._stock:
            self._stock -= quantity

    def is_in_stock(self, quantity):
        return self._stock >= quantity

    def get_price(self):
        return self._price

    def get_stock(self):
        return self._stock

class Customer(Entity):
    def __init__(self, customer_id, name, email, address):
        super().__init__(customer_id, name)
        self.email = email
        self.address = address

# Payment abstraction
class Payment(ABC):
    @abstractmethod
    def process_payment(self):
        pass

class CreditCardPayment(Payment):
    def process_payment(self):
        return "✅ Processing credit card payment..."

class PayPalPayment(Payment):
    def process_payment(self):
        return "✅ Processing PayPal payment..."

# Email validation
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Main Streamlit app
def main():
    st.title("🛒 E-commerce Product and Payment System")

    # Initialize session state
    if 'product1' not in st.session_state:
        st.session_state.product1 = Product(1, "Laptop", "High performance laptop", 1000, 50)
    if 'product2' not in st.session_state:
        st.session_state.product2 = Product(2, "Smartphone", "Latest model smartphone", 500, 100)
    if 'order_placed' not in st.session_state:
        st.session_state.order_placed = False
    if 'orders' not in st.session_state:
        st.session_state.orders = []

    product1 = st.session_state.product1
    product2 = st.session_state.product2

    # Display products
    st.subheader("📦 Available Products")
    st.write(f"1. **{product1.name}** - {product1.description} - 💲Price: ${product1.get_price()} - 🧮 Stock: {product1.get_stock()}")
    st.write(f"2. **{product2.name}** - {product2.description} - 💲Price: ${product2.get_price()} - 🧮 Stock: {product2.get_stock()}")

    # Product selection
    selected_product_name = st.selectbox("🛍️ Select a product to order", ["Laptop", "Smartphone"])
    quantity = st.number_input("📦 Enter quantity", min_value=1, max_value=20, value=1)

    # Customer Info
    st.subheader("👤 Customer Information")
    customer_name = st.text_input("Full Name")
    customer_email = st.text_input("Email")
    customer_address = st.text_area("Address")
    total_price = 0

    customer_ready = all([
        customer_name.strip(),
        customer_email.strip(),
        customer_address.strip(),
        is_valid_email(customer_email)
    ])

    product = product1 if selected_product_name == "Laptop" else product2

    if st.button("🧾 Place Order"):
        if not customer_ready:
            st.warning("⚠️ Please fill all valid customer details.")
        elif product.is_in_stock(quantity):
            customer = Customer(1, customer_name, customer_email, customer_address)
            product.update_stock(quantity)
            order_id = str(uuid.uuid4())[:8]
            total_price = quantity * product.get_price()
            order_details = {
                "order_id": order_id,
                "product": product.name,
                "quantity": quantity,
                "total": total_price,
                "customer": customer,
                "paid": False
            }
            st.session_state.orders.append(order_details)
            st.session_state.current_order = order_details
            st.session_state.order_placed = True
            st.success(f"✅ Order placed for {quantity} {product.name}(s) by {customer.name}.")
            st.info(f"🆔 Order ID: {order_id} | 💲 Total: ${total_price}")
        else:
            st.error(f"❌ Not enough stock for {product.name}. Available: {product.get_stock()}")
            st.session_state.order_placed = False

    if st.session_state.order_placed:
        st.subheader("💳 Payment Options")
        payment_method = st.radio("Select payment method", ["Credit Card", "PayPal"])

        if st.button("💰 Process Payment"):
            payment = CreditCardPayment() if payment_method == "Credit Card" else PayPalPayment()
            st.success(payment.process_payment())
            st.balloons()

            # Update payment status
            st.session_state.current_order["paid"] = True

            # Show Receipt
            order = st.session_state.current_order
            st.subheader("🧾 Receipt")
            st.write(f"**Order ID:** {order['order_id']}")
            st.write(f"**Product:** {order['product']}")
            st.write(f"**Quantity:** {order['quantity']}")
            st.write(f"**Total Amount Paid:** 💲${order['total']}")
            st.write(f"**Customer Name:** {order['customer'].name}")
            st.write(f"**Email:** {order['customer'].email}")
            st.write(f"**Address:** {order['customer'].address}")
            st.success("🎉 Thank you for your purchase!")

    # Optional: Show all past orders
    with st.expander("📜 View Order History"):
        for o in st.session_state.orders:
            st.markdown(f"- **Order ID:** {o['order_id']} | Product: {o['product']} | Qty: {o['quantity']} | Paid: {'✅' if o['paid'] else '❌'}")

if __name__ == "__main__":
    main()
