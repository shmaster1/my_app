
# Order Management Backend System

A simple Ecommerce backend project built with Python and MySQL.
It manages users, items, orders, and favorite items using a relational database design.

- **User & order management** with real-time stock validation  
- **AI shopping assistant** powered by OpenAI GPT  
- **Interactive demo** via Streamlit for fast recruiter evaluation  
- **Secure architecture** with JWT authentication and database-backed workflows  

It’s designed as a **professional portfolio project** to showcase full-stack backend development, AI integration, and scalable architecture.


---

## 💻 Tech Stack

- Python 3.x
- MySQL 8
- Docker & Docker Compose
- FastAPI (optional / if applicable)
- Streamlit
- Open AI
---

## 🔐 OpenAI / ChatGPT API Key Setup

This project uses OpenAI (ChatGPT).
If you are reviewing, cloning, or running this project locally (for example from GitHub), you must provide a valid OpenAI API key.

For security reasons, no API key is included in the repository.

---

## 🏁 Quick Start

Follow these steps to run the AI eCommerce project locally:

1️⃣ Clone the repository

git clone https://github.com/shmaster1/my_app.git
cd ecommerce-ai


2️⃣ Create a config file according to config_example.py Copy `config_example.py` to `config.py` and add your keys:


EXAMPLE_KEY=example_value


3️⃣ Start the database 🗄️

Using Docker Compose:

docker-compose -f docker-compose.yaml up


4️⃣ Initialize the Database Tables 🗄️

Once your MySQL database is running, you can create the necessary tables by executing the SQL script located in `resources/init/init.sql`
 

5️⃣ Run the backend (FastAPI)

uvicorn main:app --reload


6️⃣Run the frontend (Streamlit)

streamlit run app.py


7️⃣ Open your browser


 Load sample data (optional)

Use the following SQL inserts for users, items, orders, and favorite items to quickly populate the database for testing.

---

## 🗄️ Sample Mock Data

You can populate the database with the following sample data:


-- USERS:

INSERT INTO users (username, first_name, last_name, email, phone, country, city, hashed_password, is_registered)
VALUES
('joe', 'John', 'Doe', 'john.doe@example.com', '+49123456789', 'Germany', 'Berlin', 'hashed_pw_1', TRUE),
('smith', 'Anna', 'Smith', 'anna.smith@example.com', '+33123456789', 'France', 'Paris', 'hashed_pw_2', TRUE),
('guest1', 'Guest', 'User', 'guest1@example.com', '+00000000000', 'N/A', 'N/A', NULL, FALSE);

-- ITEMS:
INSERT INTO item (item_name, price, stock_available, image_url)
VALUES
  ('Item 1', 10.00, 5,  'https://images.pexels.com/photos/161559/background-bitter-breakfast-bright-161559.jpeg'),
  ('Item 2', 15.50, 8,  'https://images.pexels.com/photos/6848574/pexels-photo-6848574.jpeg'),
  ('Item 3', 8.75, 3,   'https://images.pexels.com/photos/102104/pexels-photo-102104.jpeg'),
  ('Item 4', 12.00, 10, 'https://images.pexels.com/photos/7223311/pexels-photo-7223311.jpeg'),
  ('Item 5', 20.00, 2,  'https://images.pexels.com/photos/4038746/pexels-photo-4038746.jpeg'),
  ('Item 6', 5.50, 7,   'https://images.pexels.com/photos/1313267/pexels-photo-1313267.jpeg'),
  ('Item 7', 18.25, 4,  'https://images.pexels.com/photos/7156088/pexels-photo-7156088.jpeg'),
  ('Item 8', 22.00, 6,  'https://images.pexels.com/photos/51312/kiwi-fruit-vitamins-healthy-eating-51312.jpeg'),
  ('Item 9', 14.75, 9,  'https://images.pexels.com/photos/1414110/pexels-photo-1414110.jpeg'),
  ('Item 10', 9.99, 1,  'https://images.pexels.com/photos/33579055/pexels-photo-33579055.png');


-- FAVORITE_ITEMS:

INSERT INTO favorite_items (user_id, item_id) VALUES
(1, 1),  -- Keyboard
(1, 3),  -- Monitor
(1, 5),  -- Item 1
(1, 7),  -- Item 3
(1, 10); -- Item 6

-- ORDERS:

INSERT INTO orders (user_id, order_date, shipping_address, total_price, status)
VALUES
(1, '2026-01-20', '123 Main St, Berlin, Germany', 69.98, 'CLOSED'),
(2, '2026-01-21', '45 Rue de Paris, Paris, France', 219.98, 'CLOSED'),
(3, '2026-01-22', 'Guest Address', 9.99, 'TEMP');

-- ORDER_ITEMS:

INSERT INTO order_items (order_id, item_id, item_quantities)
VALUES (1, 2, 3);

---

### 🚀 Future Scalability Considerations

If this system needed to scale across teams or workloads, the following domains
could be extracted into independent services:

- Authentication / Identity
- Orders (async processing)
- Inventory

This project is currently a modular monolith to avoid unnecessary complexity.

### ⚡ User Access & Prompt Limits

- The chat is available to **any user**, including non-registered visitors, making it easy to try the demo without signing up.  
- Each user session is limited to **5 prompts** to prevent overuse and ensure fair usage of the OpenAI API.  
- Prompt counts are tracked **per session** in memory. In a production scenario, counts could be persisted in a database for multi-session tracking and analytics.  
- Registration can be added in the future for personalized experiences, persistent chat history, and advanced usage tracking.


### 🧠 AI Design Decision

For this project, I used a pre-trained Large Language Model (GPT) to handle natural language understanding and conversational responses.

Training a supervised custom model for intent classification would require labeled datasets and add unnecessary complexity for this use case. Instead, I leveraged GPT’s strong reasoning capabilities and implemented a clean backend orchestration layer that routes user requests either to:

- The database (for structured ecommerce data such as items, price, and stock), or  
- The GPT API (for general conversational responses).

This approach keeps the system flexible, scalable, and aligned with modern AI application architecture.
