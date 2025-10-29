import math

class SegmentTree:
    def __init__(self, data):
        if not data:
            self.n = 0
            self.tree = []
            return
        self.n = len(data)
        self.tree = [0] * (2 * self.n)
        for i in range(self.n):
            self.tree[self.n + i] = data[i]
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = max(self.tree[2 * i], self.tree[2 * i + 1])

    def range_max(self, l, r):
        if self.n == 0:
            return None
        l += self.n
        r += self.n
        res = -math.inf
        while l < r:
            if l & 1:
                res = max(res, self.tree[l])
                l += 1
            if r & 1:
                r -= 1
                res = max(res, self.tree[r])
            l >>= 1
            r >>= 1
        return res

class RBNode:
    def __init__(self, key, value, color="red", parent=None):
        self.key = key
        self.value = value
        self.color = color
        self.parent = parent
        self.left = None
        self.right = None

class RBTree:
    def __init__(self):
        self.nil = RBNode(None, None, color="black")
        self.root = self.nil

    def insert(self, key, value):
        new_node = RBNode(key, value)
        new_node.left = self.nil
        new_node.right = self.nil

        parent = None
        current = self.root
        while current != self.nil:
            parent = current
            if key == current.key:
                current.value += value
                return
            elif key < current.key:
                current = current.left
            else:
                current = current.right

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        new_node.color = "red"
        self._fix_insert(new_node)

    def _fix_insert(self, node):
        while node.parent and node.parent.color == "red":
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle and uncle.color == "red":
                    node.parent.color = "black"
                    uncle.color = "black"
                    node.parent.parent.color = "red"
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._rotate_left(node)
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    self._rotate_right(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle and uncle.color == "red":
                    node.parent.color = "black"
                    uncle.color = "black"
                    node.parent.parent.color = "red"
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._rotate_right(node)
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    self._rotate_left(node.parent.parent)
        self.root.color = "black"

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.nil:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.nil:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def inorder(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node != self.nil:
            self.inorder(node.left, result)
            result.append((node.key, node.value))
            self.inorder(node.right, result)
        return result

    def remove(self, key, quantity):
        node = self._find_node(self.root, key)
        if node and node != self.nil:
            node.value -= quantity
            if node.value <= 0:
                # full deletion not implemented
                pass

    def _find_node(self, node, key):
        while node != self.nil:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

class OrderBook:
    def __init__(self):
        self.bids = RBTree()
        self.asks = RBTree()

    def insert_order(self, side: str, price: float, quantity: float):
        trades = []
        if side.lower() == "buy":
            while quantity > 0:
                best_ask = self.get_best_ask()
                if best_ask and price >= best_ask["price"]:
                    trade_qty = min(quantity, best_ask["quantity"])
                    trades.append({
                        "buy_price": price,
                        "sell_price": best_ask["price"],
                        "quantity": trade_qty
                    })
                    quantity -= trade_qty
                    self.remove_quantity("sell", best_ask["price"], trade_qty)
                else:
                    break
            if quantity > 0:
                self.bids.insert(price, quantity)
        else:  # sell
            while quantity > 0:
                best_bid = self.get_best_bid()
                if best_bid and price <= best_bid["price"]:
                    trade_qty = min(quantity, best_bid["quantity"])
                    trades.append({
                        "buy_price": best_bid["price"],
                        "sell_price": price,
                        "quantity": trade_qty
                    })
                    quantity -= trade_qty
                    self.remove_quantity("buy", best_bid["price"], trade_qty)
                else:
                    break
            if quantity > 0:
                self.asks.insert(price, quantity)
        return trades

    def remove_quantity(self, side: str, price: float, quantity: float):
        if side.lower() == "buy":
            self.bids.remove(price, quantity)
        else:
            self.asks.remove(price, quantity)

    def get_best_bid(self):
        bids = self.bids.inorder()
        if not bids:
            return None
        price, qty = max(bids, key=lambda x: x[0])
        return {"price": price, "quantity": qty}

    def get_best_ask(self):
        asks = self.asks.inorder()
        if not asks:
            return None
        price, qty = min(asks, key=lambda x: x[0])
        return {"price": price, "quantity": qty}

    def get_sorted_book(self, depth: int = None):
        bids = sorted(self.bids.inorder(), key=lambda x: -x[0])
        asks = sorted(self.asks.inorder(), key=lambda x: x[0])
        if depth:
            bids = bids[:depth]
            asks = asks[:depth]
        return {
            "bids": [{"price": float(p), "quantity": float(q)} for p, q in bids],
            "asks": [{"price": float(p), "quantity": float(q)} for p, q in asks],
        }
