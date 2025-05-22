class HistoryManager:
    def __init__(self):
        self.back_stack = []
        self.forward_stack = []

    def push_back(self, path):
        self.back_stack.append(path)
        self.forward_stack.clear()

    def can_go_back(self):
        return len(self.back_stack) > 0

    def can_go_forward(self):
        return len(self.forward_stack) > 0

    def go_back(self, current_path):
        if self.can_go_back():
            self.forward_stack.append(current_path)
            return self.back_stack.pop()
        return current_path

    def go_forward(self, current_path):
        if self.can_go_forward():
            self.back_stack.append(current_path)
            return self.forward_stack.pop()
        return current_path