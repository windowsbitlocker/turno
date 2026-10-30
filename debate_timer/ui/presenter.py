"""Presentation of timer state in both windows."""
from ..formatting import format_time


class PresenterMixin:
    def format_time(self, ms):
        return format_time(ms, show_tenths=self.show_milliseconds_var.get())

    def update_all_labels(self, time_up=False):
        if not self.phases:
            return

        phase = self.current_phase()
        robo_status_text = ""

        if self.robo_active:
            time_text = "¡TIEMPO!" if time_up else self.format_time(self.robo_remaining_ms)
            display_name = "Robo / refutación"
            display_team = self.robo_team
            short_warning_ms = self.safe_int(self.warning_short_sec, 10) * 1000
            near_limit = self.robo_remaining_ms <= short_warning_ms
            robo_status_text = "Robo en curso — presiona 'Terminar robo' cuando acabe"
        else:
            time_text = "¡TIEMPO!" if time_up else self.format_time(self.remaining_ms)

            if phase.kind == "conclusion" and not time_up:
                if self.steal_used_this_phase:
                    robo_status_text = self.last_steal_note
                else:
                    steal_limit_ms = self.safe_int(self.steal_limit_sec, 120) * 1000
                    elapsed_ms = phase.ms - self.remaining_ms
                    if elapsed_ms < steal_limit_ms:
                        steal_left = steal_limit_ms - elapsed_ms
                        robo_status_text = f"Robo disponible por {self.format_time(steal_left)}"
                    else:
                        robo_status_text = "Robo cerrado"

            display_name = phase.name
            display_team = phase.team
            near_limit = bool(phase.warning_at_ms and self.remaining_ms <= phase.warning_at_ms)

        self.turn_label.config(text=f"TURNO {self.phase_index + 1:02d} DE {len(self.phases):02d}")
        self.current_phase_label.config(text=display_name)
        self.current_team_label.config(text=display_team)
        self.start_pause_button.config(text="Pausar" if self.running else "Iniciar")
        self.previous_button.state(["disabled"] if self.phase_index == 0 else ["!disabled"])
        self.next_button.state(["disabled"] if self.phase_index == len(self.phases) - 1 else ["!disabled"])
        upcoming = self.phases[self.phase_index + 1] if self.phase_index + 1 < len(self.phases) else None
        self.up_next_label.config(text=f"{upcoming.name} · {upcoming.team}" if upcoming else "Fin del debate")
        if phase.kind == "conclusion":
            if not self.steal_panel.winfo_manager():
                self.steal_panel.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        else:
            self.steal_panel.grid_remove()
        steal_limit = self.safe_int(self.steal_limit_sec, 120) * 1000
        available = (phase.kind == "conclusion" and not self.robo_active
                     and not self.steal_used_this_phase and self.remaining_ms > 0
                     and phase.ms - self.remaining_ms < steal_limit)
        self.steal_button.state(["!disabled"] if available else ["disabled"])
        self.end_steal_button.state(["!disabled"] if self.robo_active else ["disabled"])
        if self.robo_active:
            self.steal_button.grid_remove()
            self.end_steal_button.grid()
        else:
            self.end_steal_button.grid_remove()
            self.steal_button.grid()
        self.current_time_label.config(text=time_text)

        if hasattr(self, "robo_status_label"):
            control_note = robo_status_text
            if self.robo_active:
                control_note = "La conclusión está en pausa."
            elif self.steal_used_this_phase:
                control_note = "Robo utilizado en este turno."
            self.robo_status_label.config(text=control_note)

        if hasattr(self, "status_label"):
            if time_up:
                self.status_label.config(text="Tiempo terminado", bg=self.CARD_BG, fg=self.DANGER)
            elif self.robo_active:
                self.status_label.config(text="Robo en curso" if self.running else "Robo en pausa", bg=self.CARD_BG, fg=self.ACCENT)
            elif self.running:
                self.status_label.config(text="En curso", bg=self.CARD_BG, fg=self.SUCCESS)
            else:
                self.status_label.config(text="Pausado / listo", bg=self.CARD_BG, fg=self.TEXT_SOFT)

        self.display_title_label.config(text=self.title_var.get().strip() or "Temporizador de Debate")
        self.display_phase_label.config(text=display_name)
        self.display_team_label.config(text=display_team)
        self.display_timer_label.config(text=time_text)
        self.display_robo_label.config(text=robo_status_text)

        if time_up:
            self.display_timer_label.config(fg="#ef9a90")
        elif near_limit:
            self.display_timer_label.config(fg=self.WARNING)
        else:
            self.display_timer_label.config(fg="#ffffff")
