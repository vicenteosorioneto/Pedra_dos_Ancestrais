# core/scene_manager.py — gerenciador de cenas com pilha

class SceneManager:
    def __init__(self):
        self._stack = []
        self._pending = None
        self._pending_action = None

    def push(self, scene):
        """Empilha cena (pausa a anterior)."""
        self._pending = scene
        self._pending_action = "push"

    def pop(self):
        """Remove cena do topo, retorna para a anterior."""
        self._pending_action = "pop"

    def replace(self, scene):
        """Substitui cena atual (transição de ato)."""
        self._pending = scene
        self._pending_action = "replace"

    def apply_pending(self):
        """Aplica mudança de cena no início do próximo frame."""
        if self._pending_action is None:
            return
        action = self._pending_action
        scene  = self._pending
        self._pending_action = None
        self._pending = None

        if action == "push" and scene:
            self._stack.append(scene)
            scene.on_enter()
        elif action == "pop" and self._stack:
            old = self._stack.pop()
            old.on_exit()
            if self._stack:
                self._stack[-1].on_resume()
        elif action == "replace" and scene:
            if self._stack:
                old = self._stack.pop()
                old.on_exit()
            self._stack.append(scene)
            scene.on_enter()

    @property
    def current(self):
        return self._stack[-1] if self._stack else None

    @property
    def is_empty(self):
        return len(self._stack) == 0
