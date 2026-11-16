package com.citas.turnos_service.controller;

import com.citas.turnos_service.dto.TurnoRequestDTO;
import com.citas.turnos_service.model.Turno;
import com.citas.turnos_service.service.TurnoService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Objects;

@RestController
@RequestMapping("/turnos")
public class TurnoController {

    private final TurnoService turnoService;

    public TurnoController(TurnoService turnoService) {
        this.turnoService = turnoService;
    }

    @PostMapping
    public ResponseEntity<Turno> crearTurno(
            @Valid @RequestBody TurnoRequestDTO dto,
            @AuthenticationPrincipal Jwt jwt) {
        if (!esAdmin(jwt)) {
            dto.setIdUsuario(idUsuario(jwt));
        }
        return ResponseEntity.status(HttpStatus.CREATED).body(turnoService.crearTurno(dto));
    }

    @GetMapping
    public ResponseEntity<List<Turno>> obtenerTodosTurnos(
            @RequestParam(required = false) Long idUsuario,
            @AuthenticationPrincipal Jwt jwt) {
        if (idUsuario == null) {
            requireAdmin(jwt);
            return ResponseEntity.ok(turnoService.obtenerTodosTurnos());
        }
        requireOwnerOrAdmin(idUsuario, jwt);
        return ResponseEntity.ok(turnoService.obtenerTurnosUsuario(idUsuario));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Turno> obtenerTurnoPorId(
            @PathVariable Long id,
            @AuthenticationPrincipal Jwt jwt) {
        Turno turno = turnoService.obtenerTurnoPorId(id);
        if (turno == null) {
            return ResponseEntity.notFound().build();
        }
        requireOwnerOrAdmin(turno.getIdUsuario(), jwt);
        return ResponseEntity.ok(turno);
    }

    @GetMapping("/usuario/{idUsuario}")
    public List<Turno> obtenerTurnosUsuario(
            @PathVariable Long idUsuario,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(idUsuario, jwt);
        return turnoService.obtenerTurnosUsuario(idUsuario);
    }

    @PutMapping("/{idTurno}")
    public Turno actualizarTurno(
            @PathVariable Long idTurno,
            @Valid @RequestBody TurnoRequestDTO dto,
            @AuthenticationPrincipal Jwt jwt) {
        Turno existing = getTurnoOrThrow(idTurno);
        requireOwnerOrAdmin(existing.getIdUsuario(), jwt);
        if (!esAdmin(jwt)) {
            dto.setIdUsuario(idUsuario(jwt));
        }
        return turnoService.actualizarTurno(idTurno, dto);
    }

    @PutMapping("/cancelar/{idTurno}")
    public Turno cancelarTurno(
            @PathVariable Long idTurno,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(getTurnoOrThrow(idTurno).getIdUsuario(), jwt);
        return turnoService.cancelarTurno(idTurno);
    }

    @DeleteMapping("/{idTurno}")
    public void eliminarTurno(
            @PathVariable Long idTurno,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(getTurnoOrThrow(idTurno).getIdUsuario(), jwt);
        turnoService.eliminarTurno(idTurno);
    }

    @GetMapping("/especialidades")
    public List<String> obtenerEspecialidades() {
        return turnoService.obtenerEspecialidades();
    }

    @GetMapping("/doctores")
    public List<String> obtenerDoctores() {
        return turnoService.obtenerDoctores();
    }

    @GetMapping("/doctores/{especialidad}")
    public List<String> obtenerDoctoresPorEspecialidad(@PathVariable String especialidad) {
        return turnoService.obtenerDoctoresPorEspecialidad(especialidad);
    }

    @GetMapping("/horarios/{doctor}")
    public List<String> obtenerHorarios(@PathVariable String doctor) {
        return turnoService.obtenerHorariosDisponibles(doctor);
    }

    private Turno getTurnoOrThrow(Long id) {
        Turno turno = turnoService.obtenerTurnoPorId(id);
        if (turno == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Turno no encontrado");
        }
        return turno;
    }

    private void requireOwnerOrAdmin(Long ownerId, Jwt jwt) {
        if (!esAdmin(jwt) && !Objects.equals(ownerId, idUsuario(jwt))) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "No autorizado");
        }
    }

    private void requireAdmin(Jwt jwt) {
        if (!esAdmin(jwt)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Se requiere rol ADMIN");
        }
    }

    private boolean esAdmin(Jwt jwt) {
        return "ADMIN".equals(jwt.getClaimAsString("role"));
    }

    private Long idUsuario(Jwt jwt) {
        Number userId = jwt.getClaim("userId");
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Token sin identificador de usuario");
        }
        return userId.longValue();
    }
}
