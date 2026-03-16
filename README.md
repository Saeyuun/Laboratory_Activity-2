# 🍚 Toppings Rice Stall — OOP Food Ordering System

A console-based food ordering program in Python. The stall sells steamed rice with **Chicken**, **Beef**, or **Pork** toppings, each in **Plain** or **two signature flavors**.

```bash
python rice_toppings_stall.py
```

---

## 1. Program Design and Class Structure

The program uses four classes, each with a single responsibility:

| Class | Responsibility |
|---|---|
| `MenuItem` | Stores a dish's topping, flavor, and price |
| `OrderItem` | Pairs a `MenuItem` with a quantity and computes line subtotals |
| `Order` | Manages the full order — adds/removes items, computes totals, prints receipt |
| `FoodStall` | Controller — handles all user interaction and drives the session |

This structure follows the **Single Responsibility Principle**: each class owns one job. `MenuItem` never needs to know about quantities; `Order` never needs to handle keyboard input. Separating the controller (`FoodStall`) from the domain classes also means the business logic could be reused in a different interface (web, GUI) without modification.

---

## 2. User Input and Exception Handling

All input flows through three centralized helper methods — `_get_int()`, `_get_name()`, and `_get_yes_no()` — so validation logic is never repeated. Each wraps its `input()` call in a `try-except` loop that catches `ValueError` (blank input, wrong type, out-of-range numbers, invalid characters) and re-prompts the user with a clear message instead of crashing.

A second layer of `try-except` wraps the item-adding flow to catch business-rule violations (e.g., zero quantity) and an `Exception` catch-all to prevent any runtime error from terminating the program mid-session. The cash payment loop uses the same pattern, catching non-numeric input and insufficient payment until the transaction is valid.

---

## 3. Limitation and Proposed Improvement

**Limitation:** All order data is lost when the program exits. There is no order history, daily sales summary, or ability to review past transactions.

**Improvement:** Add an `OrderHistory` class using a **class-level attribute** to collect completed orders during a session, and a `DataStore` class to serialize them to a JSON file between sessions. This introduces two OOP concepts not yet used — **class attributes/class methods** and **inheritance** (a `DiscountedOrder` subclass could override `compute_totals()` instead of storing discount logic as a plain float). Error handling would also expand to cover `OSError`, `FileNotFoundError`, and `json.JSONDecodeError` — file-level errors the current program never encounters.

---
