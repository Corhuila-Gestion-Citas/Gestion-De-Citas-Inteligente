package com.citas.audit_service.controller;

import com.citas.audit_service.dto.AuditRequestDTO;
import com.citas.audit_service.model.AuditLog;
import com.citas.audit_service.service.AuditLogService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

@RestController
@RequestMapping("/audit")
public class AuditLogController {

    private final AuditLogService auditLogService;

    public AuditLogController(AuditLogService auditLogService) {
        this.auditLogService = auditLogService;
    }

    @PostMapping
    public ResponseEntity<AuditLog> crearRegistro(
            @Valid @RequestBody AuditRequestDTO dto,
            @AuthenticationPrincipal Jwt jwt) {
        AuditLog auditLog = auditLogService.crearRegistro(dto, idUsuario(jwt));

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(auditLog);
    }

    @GetMapping
    public ResponseEntity<List<AuditLog>> obtenerTodos(@AuthenticationPrincipal Jwt jwt) {
        requireAdmin(jwt);
        return ResponseEntity.ok(auditLogService.obtenerTodos());
    }

    @GetMapping("/usuario/{idUsuario}")
    public ResponseEntity<List<AuditLog>> obtenerPorUsuario(
            @PathVariable Long idUsuario,
            @AuthenticationPrincipal Jwt jwt) {
        requireOwnerOrAdmin(idUsuario, jwt);
        return ResponseEntity.ok(auditLogService.obtenerPorUsuario(idUsuario));
    }

    @GetMapping("/accion/{accion}")
    public ResponseEntity<List<AuditLog>> obtenerPorAccion(
            @PathVariable String accion,
            @AuthenticationPrincipal Jwt jwt) {
        requireAdmin(jwt);
        return ResponseEntity.ok(auditLogService.obtenerPorAccion(accion));
    }

    @GetMapping("/servicio/{servicioOrigen}")
    public ResponseEntity<List<AuditLog>> obtenerPorServicio(
            @PathVariable String servicioOrigen,
            @AuthenticationPrincipal Jwt jwt) {
        requireAdmin(jwt);
        return ResponseEntity.ok(auditLogService.obtenerPorServicio(servicioOrigen));
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> obtenerEstadisticas(@AuthenticationPrincipal Jwt jwt) {
        requireAdmin(jwt);
        Map<String, Object> respuesta = new LinkedHashMap<>();
        respuesta.put("totalRegistros", auditLogService.contarRegistros());
        respuesta.put("servicio", "audit-service");
        respuesta.put("baseDatos", "MongoDB");

        return ResponseEntity.ok(respuesta);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> respuesta = new LinkedHashMap<>();
        respuesta.put("status", "OK");
        respuesta.put("service", "audit-service");
        respuesta.put("database", "MongoDB");

        return ResponseEntity.ok(respuesta);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminarRegistro(
            @PathVariable String id,
            @AuthenticationPrincipal Jwt jwt) {
        requireAdmin(jwt);
        auditLogService.eliminarRegistro(id);
        return ResponseEntity.noContent().build();
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
