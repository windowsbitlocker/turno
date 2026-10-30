"""Operator-controlled robo eligibility, duration, and deduction rules."""
from tkinter import messagebox


class RebuttalMixin:
    def start_steal(self):
        phase = self.current_phase()

        if self.robo_active:
            messagebox.showwarning("Robo en curso", "Ya hay un robo corriendo. Usa 'Terminar robo' primero.")
            return

        if phase.kind != "conclusion":
            messagebox.showwarning("No disponible", "El robo solo se usa en la etapa de conclusión.")
            return

        steal_limit_ms = self.safe_int(self.steal_limit_sec, 120) * 1000
        elapsed_ms = phase.ms - self.remaining_ms

        if elapsed_ms >= steal_limit_ms:
            messagebox.showwarning("Demasiado tarde", "El robo ya no está permitido.")
            return

        if self.steal_used_this_phase:
            messagebox.showwarning("Ya fue usado", "El robo ya fue usado en esta conclusión.")
            return

        if self.remaining_ms <= 0:
            messagebox.showwarning("Sin tiempo", "No queda tiempo en la conclusión para robar.")
            return

        self.pause()

        favor = self.team_favor_var.get().strip() or "Equipo a favor"
        against = self.team_against_var.get().strip() or "Equipo en contra"
        other_team = against if phase.team == favor else favor

        requested_steal_ms = max(1_000, self.safe_int(self.steal_min, 1) * 60_000)
        # El tope de robo no puede superar el tiempo que realmente queda.
        cap_ms = min(requested_steal_ms, self.remaining_ms)

        # El robo NO quita el minuto entero de inmediato: arranca su propio
        # conteo (hasta el tope). Solo se descuenta de la conclusión lo que
        # realmente se use, no el tope completo.
        self.robo_active = True
        self.robo_team = other_team
        self.robo_remaining_ms = cap_ms
        self.robo_max_ms = cap_ms
        self.steal_used_this_phase = True
        self.last_steal_note = ""

        self.start()

    def finish_steal(self, used_ms=None):
        """Cierra el robo y descuenta de la conclusión solo el tiempo usado."""
        if not self.robo_active:
            return

        if used_ms is None:
            used_ms = self.robo_max_ms - self.robo_remaining_ms
        used_ms = max(0, min(int(used_ms), self.robo_max_ms))

        self.remaining_ms = max(0, self.remaining_ms - used_ms)
        self.last_steal_note = f"ROBO: {self.robo_team} usó {used_ms // 1000}s (restados de la conclusión)"

        self.robo_active = False
        self.robo_team = ""
        self.robo_remaining_ms = 0
        self.robo_max_ms = 0

    def end_steal_now(self):
        if not self.robo_active:
            messagebox.showinfo("Sin robo activo", "No hay ningún robo corriendo en este momento.")
            return

        self.pause()
        self.finish_steal()
        self.update_all_labels()
