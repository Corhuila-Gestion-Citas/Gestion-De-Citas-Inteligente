package com.citas.notifications_service.controller;

import com.citas.notifications_service.dto.NotificacionRequestDTO;
import com.citas.notifications_service.model.Notificacion;
import com.citas.notifications_service.service.NotificacionService;
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
@RequestMapping("/notifications")
public class NotificacionController {

    private final NotificacionService notificacionService;

    public NotificacionController(NotificacionService notificacionService) {
        this.notificacionService = notificacionService;
    }

    @PostMapping
    public ResponseEntity<Notificacion> crearNotificacion(
            @Valid @RequestBody NotificacionRequestDTO dto,
            @AuthenticationPrincipal Jwt jwt) {
        dto.setIdUsuario(idUsuario(jwt));
        Notificacion notificacion = notificacionService.crearNotificacion(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(notificacion);
    }

    @GetMapping
    public ResponseEntity<List<Notificacion>> obtenerTodas(@AuthenticationPrincipal Jwt jwt) {
        requireAdmin(jwt);
        return ResponseEntity.ok(notificacionService.obtenerTodas());
    }

    @GetMapping("/usuario/{idUsuario}")
    public ResponseEntity<List<Notificacion>> obtenerPorUsuario(
            @PathVariable Long idUsuario,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(idUsuario, jwt);
        return ResponseEntity.ok(notificacionService.obtenerPorUsuario(idUsuario));
    }

    @PutMapping("/{id}/leida")
    public ResponseEntity<Notificacion> marcarComoLeida(
            @PathVariable Long id,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(getNotificacionOrThrow(id).getIdUsuario(), jwt);
        return ResponseEntity.ok(notificacionService.marcarComoLeida(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminarNotificacion(
            @PathVariable Long id,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(getNotificacionOrThrow(id).getIdUsuario(), jwt);
        notificacionService.eliminarNotificacion(id);
        return ResponseEntity.noContent().build();
    }

    private Notificacion getNotificacionOrThrow(Long id) {
        return notificacionService.obtenerPorId(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Notificación no encontrada"));
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
