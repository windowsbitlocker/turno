"""Countdown scheduling, phase navigation, and operator-controlled robo rules."""
import time
from .models import PhaseSettings
from .phases import build_phases
from .templates import compile_template


class TimingMixin:
    def phase_settings(self):
        return PhaseSettings(
            favor=self.team_favor_var.get().strip() or "Equipo a favor",
            against=self.team_against_var.get().strip() or "Equipo en contra",
            prep_min=self.safe_int(self.prep_min, 1),
            opening_min=self.safe_int(self.opening_min, 3),
            question_sec=self.safe_int(self.question_sec, 40),
            answer_min=self.safe_int(self.answer_min, 1),
            final_prep_min=self.safe_int(self.final_prep_min, 5),
            conclusion_min=self.safe_int(self.conclusion_min, 3),
            jury_min=self.safe_int(self.jury_min, 5),
            opening_warning_sec=self.safe_int(self.warning_opening_sec, 30),
            short_warning_sec=self.safe_int(self.warning_short_sec, 10),
            jury_warning_sec=self.safe_int(self.warning_jury_sec, 60),
        )

    def rebuild_phases(self):
        if self.active_template is not None:
            self.phases = compile_template(self.active_template)
        else:
            self.phases = build_phases(self.phase_settings())

    def load_phase(self, index):
        if not self.phases:
            self.rebuild_phases()

        self.phase_index = max(0, min(index, len(self.phases) - 1))
        phase = self.phases[self.phase_index]
        self.remaining_ms = phase.ms
        self.steal_used_this_phase = False
        self.last_steal_note = ""
        self.robo_active = False
        self.robo_team = ""
        self.robo_remaining_ms = 0
        self.robo_max_ms = 0
        self.robo_deduct = True
        self.last_tick_time = None
        self.update_all_labels()

    def current_phase(self):
        return self.phases[self.phase_index]

    def start(self):
        if self.running:
            return
        self.running = True
        self.last_tick_time = time.perf_counter()
        self.tick()

    def pause(self):
        self.settle_clock()
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.last_tick_time = None
        self.update_all_labels()

    def settle_clock(self):
        """Cuenta también el tiempo entre el último tick y un botón del operador."""
        if not self.running or self.last_tick_time is None:
            return
        elapsed = max(0, int((time.perf_counter() - self.last_tick_time) * 1000))
        self.last_tick_time += elapsed / 1000
        if self.robo_active:
            self.robo_remaining_ms = max(0, self.robo_remaining_ms - elapsed)
            if self.robo_remaining_ms == 0:
                self.finish_steal(used_ms=self.robo_max_ms)
                self.running = False
        else:
            self.remaining_ms = max(0, self.remaining_ms - elapsed)

    def tick(self):
        if not self.running:
            return

        now = time.perf_counter()
        if self.last_tick_time is None:
            self.last_tick_time = now

        elapsed_ms = int((now - self.last_tick_time) * 1000)
        self.last_tick_time += elapsed_ms / 1000

        if self.robo_active:
            self.robo_remaining_ms -= elapsed_ms

            if self.robo_remaining_ms <= 0:
                self.robo_remaining_ms = 0
                self.running = False
                # Se agotó el tope del robo: se usó completo. Esto NO significa
                # que el tiempo de la conclusión se haya terminado.
                self.finish_steal(used_ms=self.robo_max_ms)
                self.update_all_labels()
                try:
                    self.root.bell()
                except Exception:
                    pass
                return

            self.update_all_labels()
            self.after_id = self.root.after(30, self.tick)
            return

        self.remaining_ms -= elapsed_ms

        if self.remaining_ms <= 0:
            self.remaining_ms = 0
            self.running = False
            self.update_all_labels(time_up=True)
            try:
                self.root.bell()
            except Exception:
                pass
            return

        self.update_all_labels()
        self.after_id = self.root.after(30, self.tick)

    def reset_current(self):
        self.pause()
        self.load_phase(self.phase_index)

    def next_phase(self):
        self.pause()
        self.load_phase(self.phase_index + 1)

    def previous_phase(self):
        self.pause()
        self.load_phase(self.phase_index - 1)

    def adjust_time(self, amount_ms):
        self.settle_clock()
        self.remaining_ms = max(0, self.remaining_ms + amount_ms)
        self.update_all_labels()
