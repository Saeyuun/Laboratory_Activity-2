import os
import datetime


#  MENU DATA  (topping → [plain, flavor1, flavor2])
MENU = {
    "Chicken": {
        "Plain":       55.00,
        "Teriyaki":    70.00,
        "Spicy Garlic": 70.00,
    },
    "Beef": {
        "Plain":       65.00,
        "Black Pepper": 80.00,
        "Bulgogi":     80.00,
    },
    "Pork": {
        "Plain":       60.00,
        "Adobo":       75.00,
        "Sweet BBQ":   75.00,
    },
}

SEPARATOR = "─" * 50

#  CLASS 1 : MenuItem
#  Represents one dish (rice + topping + flavor)
class MenuItem:
    def __init__(self, topping: str, flavor: str, price: float):
        self.topping = topping
        self.flavor  = flavor
        self.price   = price

    # ── Method 1 ──────────────────────────────
    def get_display_name(self) -> str:
        if self.flavor == "Plain":
            return f"Plain {self.topping} Rice"
        return f"{self.topping} {self.flavor} Rice"

    # ── Method 2 ──────────────────────────────
    def apply_discount(self, percent: float) -> float:
        if not (0 <= percent <= 100):
            raise ValueError("Discount must be between 0 and 100.")
        return round(self.price * (1 - percent / 100), 2)

    def __str__(self) -> str:
        return f"{self.get_display_name():<30} ₱{self.price:>6.2f}"

    def __repr__(self) -> str:
        return (f"MenuItem(topping={self.topping!r}, "
                f"flavor={self.flavor!r}, price={self.price})")

#  CLASS 2 : OrderItem
#  One line in a customer's order (item + qty)
class OrderItem:

    def __init__(self, menu_item: MenuItem, quantity: int):
        self.menu_item = menu_item
        self.quantity  = quantity

    # ── Method 1 ──────────────────────────────
    def get_subtotal(self) -> float:
        """Returns price × quantity for this line item."""
        return round(self.menu_item.price * self.quantity, 2)

    # ── Method 2 ──────────────────────────────
    def update_quantity(self, new_qty: int) -> None:
        if new_qty <= 0:
            raise ValueError("Quantity must be at least 1.")
        self.quantity = new_qty

    def __str__(self) -> str:
        return (f"{self.menu_item.get_display_name():<30} "
                f"x{self.quantity:<3}  ₱{self.get_subtotal():>7.2f}")



#  CLASS 3 : Order
#  Manages a customer's complete order session
class Order:

    TAX_RATE = 0.00            # set to e.g. 0.12 to enable VAT

    def __init__(self, customer_name: str, discount_pct: float = 0.0):
        self.customer_name = customer_name
        self.discount_pct  = discount_pct
        self.items: list[OrderItem] = []
        self._order_time   = datetime.datetime.now()

    # ── Method 1 ──────────────────────────────
    def add_item(self, menu_item: MenuItem, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        # Check if item already exists → just bump quantity
        for existing in self.items:
            if (existing.menu_item.topping == menu_item.topping and
                    existing.menu_item.flavor == menu_item.flavor):
                existing.update_quantity(existing.quantity + quantity)
                return

        self.items.append(OrderItem(menu_item, quantity))

    # ── Method 2 ──────────────────────────────
    def compute_totals(self) -> dict:
        subtotal     = sum(oi.get_subtotal() for oi in self.items)
        discount_amt = round(subtotal * self.discount_pct / 100, 2)
        taxable      = subtotal - discount_amt
        tax          = round(taxable * self.TAX_RATE, 2)
        grand_total  = round(taxable + tax, 2)
        return {
            "subtotal":     subtotal,
            "discount_amt": discount_amt,
            "taxable":      taxable,
            "tax":          tax,
            "grand_total":  grand_total,
        }

    # ── Method 3 ──────────────────────────────
    def print_receipt(self) -> None:
        """Prints a formatted receipt to the console."""
        totals = self.compute_totals()

        print()
        print("=" * 50)
        print("           TOPPINGS RICE STALL  ")
        print("=" * 50)
        print(f"  Customer : {self.customer_name}")
        print(f"  Date     : {self._order_time.strftime('%b %d, %Y  %I:%M %p')}")
        print(SEPARATOR)
        print(f"  {'ITEM':<30} {'QTY':<4} {'AMOUNT':>8}")
        print(SEPARATOR)

        if not self.items:
            print("  (no items)")
        else:
            for oi in self.items:
                print(f"  {oi}")

        print(SEPARATOR)
        print(f"  {'Subtotal':<38} ₱{totals['subtotal']:>7.2f}")

        if self.discount_pct > 0:
            print(f"  {'Discount (' + str(self.discount_pct) + '%)':<38} "
                  f"-₱{totals['discount_amt']:>6.2f}")

        if self.TAX_RATE > 0:
            print(f"  {'VAT (' + str(int(self.TAX_RATE*100)) + '%)':<38} "
                  f"₱{totals['tax']:>7.2f}")

        print(SEPARATOR)
        print(f"  {'TOTAL':<38} ₱{totals['grand_total']:>7.2f}")
        print("=" * 50)
        print("    Thank you! Enjoy your meal!  😊")
        print("=" * 50)
        print()

    # ── Method 4 ──────────────────────────────
    def remove_item(self, index: int) -> None:
        if not (1 <= index <= len(self.items)):
            raise IndexError(
                f"Invalid item number. Choose between 1 and {len(self.items)}.")
        removed = self.items.pop(index - 1)
        print(f"  ✓ Removed: {removed.menu_item.get_display_name()}")

    def is_empty(self) -> bool:
        """Returns True when no items have been added yet."""
        return len(self.items) == 0

    def __str__(self) -> str:
        count = len(self.items)
        total = self.compute_totals()["grand_total"]
        return (f"Order for {self.customer_name!r} | "
                f"{count} item(s) | Total: ₱{total:.2f}")

#  CLASS 4 : FoodStall  (controller / UI layer)
#  Drives all console interaction
class FoodStall:
    STALL_NAME    = "Toppings Ta Bai"
    SENIOR_DISC   = 20.0    # % discount for senior / PWD

    def __init__(self):
        # Build MenuItem catalog once from MENU dict
        self._catalog: dict[str, dict[str, MenuItem]] = {}
        for topping, flavors in MENU.items():
            self._catalog[topping] = {}
            for flavor, price in flavors.items():
                self._catalog[topping][flavor] = MenuItem(topping, flavor, price)

    # ── Helper : clear screen ─────────────────
    @staticmethod
    def _clear():
        os.system("cls" if os.name == "nt" else "clear")

    # ── Helper : safe integer input ───────────
    @staticmethod
    def _get_int(prompt: str,
                 min_val: int = 1,
                 max_val: int = 999) -> int:
        while True:
            try:
                raw = input(prompt).strip()
                if not raw:
                    raise ValueError("Input cannot be blank.")
                value = int(raw)
                if not (min_val <= value <= max_val):
                    raise ValueError(
                        f"Please enter a number between {min_val} and {max_val}.")
                return value
            except ValueError as err:
                print(f"  ⚠  Invalid input – {err}  Try again.")

    # ── Helper : safe yes/no ──────────────────
    @staticmethod
    def _get_yes_no(prompt: str) -> bool:
        """Returns True for 'y', False for 'n'. Loops on bad input."""
        while True:
            try:
                raw = input(prompt).strip().lower()
                if raw not in ("y", "n", "yes", "no"):
                    raise ValueError("Please type  y  or  n.")
                return raw.startswith("y")
            except ValueError as err:
                print(f"  ⚠  {err}")

    # ── Helper : safe name input ──────────────
    @staticmethod
    def _get_name(prompt: str) -> str:
        """Ensures name is not blank and contains only valid characters."""
        while True:
            try:
                name = input(prompt).strip()
                if not name:
                    raise ValueError("Name cannot be blank.")
                if not all(c.isalpha() or c in (" ", ".", "-", "'")
                           for c in name):
                    raise ValueError(
                        "Name may only contain letters, spaces, "
                        "periods, hyphens, or apostrophes.")
                return name
            except ValueError as err:
                print(f"  ⚠  {err}  Try again.")

    # ── Method 1 : show full menu ─────────────
    def display_menu(self) -> None:
        """Prints the complete menu grouped by topping."""
        print()
        print("=" * 50)
        print(f"        🍽  {self.STALL_NAME.upper()}  🍽")
        print("     All prices include steamed rice (1 cup)")
        print("=" * 50)

        topping_list = list(self._catalog.keys())
        for t_idx, topping in enumerate(topping_list, start=1):
            print(f"\n  [{t_idx}] {topping.upper()} TOPPINGS")
            print(f"  {'─'*44}")
            flavor_list = list(self._catalog[topping].values())
            for f_idx, item in enumerate(flavor_list, start=1):
                print(f"      ({f_idx}) {item}")

        print()
        print(f"  {'─'*44}")
        print(f"  Senior / PWD discount: {self.SENIOR_DISC:.0f}% off subtotal")
        print("=" * 50)

    # ── Method 2 : pick one MenuItem ─────────
    def _select_item(self) -> MenuItem:
        topping_list = list(self._catalog.keys())
        flavor_lists = {t: list(self._catalog[t].keys())
                        for t in topping_list}

        # -- choose topping --
        print(f"\n  Choose a topping:")
        for i, t in enumerate(topping_list, 1):
            print(f"    [{i}] {t}")

        t_choice = self._get_int(
            "  Enter number: ", 1, len(topping_list))
        chosen_topping = topping_list[t_choice - 1]

        # -- choose flavor --
        flavors = flavor_lists[chosen_topping]
        print(f"\n  Choose a flavor for {chosen_topping}:")
        for i, f in enumerate(flavors, 1):
            item = self._catalog[chosen_topping][f]
            print(f"    [{i}] {item}")

        f_choice = self._get_int(
            "  Enter number: ", 1, len(flavors))
        chosen_flavor = flavors[f_choice - 1]

        return self._catalog[chosen_topping][chosen_flavor]

    # ── Method 3 : view / edit current order ──
    def _view_order(self, order: Order) -> None:
        """Displays items currently in the order with remove option."""
        if order.is_empty():
            print("\n  Your order is empty.\n")
            return

        print(f"\n  Current Order for {order.customer_name}:")
        print(f"  {SEPARATOR}")
        for i, oi in enumerate(order.items, 1):
            print(f"  [{i}] {oi}")
        print(f"  {SEPARATOR}")
        totals = order.compute_totals()
        print(f"  Subtotal: ₱{totals['subtotal']:.2f}")

        # Offer removal
        if self._get_yes_no("\n  Remove an item?  (y/n): "):
            idx = self._get_int(
                "  Enter item number to remove: ",
                1, len(order.items))
            try:
                order.remove_item(idx)
            except IndexError as err:
                print(f"  ⚠  {err}")

    # ── Method 4 : main ordering loop ─────────
    def run(self) -> None:
        """
        Entry point.  Drives the full order session:
          1. Welcome screen
          2. Customer name + discount check
          3. Ordering loop (add items, view order, checkout)
          4. Receipt print
        """
        self._clear()
        print("\n" + "=" * 50)
        print("   Welcome to  🍚  Toppings Rice Stall  🍚")
        print("=" * 50)

        # ── Get customer name ─────────────────
        customer_name = self._get_name("\n  Enter your name: ")

        # ── Senior / PWD discount? ────────────
        disc = 0.0
        is_senior = self._get_yes_no(
            "  Are you a Senior Citizen or PWD? (y/n): ")
        if is_senior:
            disc = self.SENIOR_DISC
            print(f"  ✓ {disc:.0f}% discount applied to your order.")

        order = Order(customer_name, discount_pct=disc)

        # ── Ordering loop ─────────────────────
        while True:
            print("\n" + SEPARATOR)
            print("  MAIN MENU")
            print("  [1] View / Browse Menu")
            print("  [2] Add Item to Order")
            print("  [3] View / Edit Current Order")
            print("  [4] Checkout & Print Receipt")
            print("  [5] Cancel & Exit")
            print(SEPARATOR)

            choice = self._get_int("  Choose an option: ", 1, 5)

            # ---- 1. Show menu ----------------
            if choice == 1:
                self.display_menu()

            # ---- 2. Add item -----------------
            elif choice == 2:
                self.display_menu()
                try:
                    selected_item = self._select_item()
                    qty = self._get_int(
                        f"\n  How many servings of "
                        f"'{selected_item.get_display_name()}'? ",
                        1, 99)
                    order.add_item(selected_item, qty)
                    print(f"\n  ✓ Added {qty}x "
                          f"{selected_item.get_display_name()} "
                          f"to your order.")
                except ValueError as err:
                    print(f"\n  ⚠  Could not add item – {err}")
                except Exception as err:
                    print(f"\n  ⚠  Unexpected error – {err}")

            # ---- 3. View / edit order --------
            elif choice == 3:
                self._view_order(order)

            # ---- 4. Checkout -----------------
            elif choice == 4:
                if order.is_empty():
                    print("\n  ⚠  You haven't added anything yet!")
                    continue

                # Optional: apply a promo discount
                promo = self._get_yes_no(
                    "\n  Do you have a promo code? (y/n): ")
                if promo:
                    try:
                        pct = self._get_int(
                            "  Enter discount % (1–50): ", 1, 50)
                        # Stack with senior discount
                        combined = min(order.discount_pct + pct, 50)
                        order.discount_pct = combined
                        print(f"  ✓ Total discount set to {combined:.0f}%.")
                    except ValueError as err:
                        print(f"  ⚠  Promo error – {err}. "
                              f"Proceeding without extra discount.")

                order.print_receipt()

                # Compute payment
                grand = order.compute_totals()["grand_total"]
                while True:
                    try:
                        cash_raw = input(
                            f"  Enter cash payment (₱): ").strip()
                        if not cash_raw:
                            raise ValueError("Payment cannot be blank.")
                        cash = float(cash_raw)
                        if cash <= 0:
                            raise ValueError(
                                "Payment must be a positive amount.")
                        if cash < grand:
                            raise ValueError(
                                f"Insufficient. Total is ₱{grand:.2f}.")
                        change = round(cash - grand, 2)
                        print(f"\n  Cash Tendered : ₱{cash:>9.2f}")
                        print(f"  Change        : ₱{change:>9.2f}")
                        print("\n  ✅  Payment complete! Have a great meal!\n")
                        break
                    except ValueError as err:
                        print(f"  ⚠  {err}  Try again.")

                break   # End ordering loop after successful checkout

            # ---- 5. Cancel / exit ------------
            elif choice == 5:
                confirm = self._get_yes_no(
                    "\n  Are you sure you want to cancel? (y/n): ")
                if confirm:
                    print("\n  Order cancelled. Goodbye!\n")
                    break

        print("  Thank you for visiting Toppings Rice Stall! 🍚\n")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    stall = FoodStall()
    stall.run()