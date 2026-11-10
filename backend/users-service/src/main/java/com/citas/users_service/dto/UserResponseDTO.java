package com.citas.users_service.dto;

import com.citas.users_service.model.Role;
import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class UserResponseDTO {

    private Long id;
    private String nombre;
    private String email;
    private Role rol;
    private String token;

    public UserResponseDTO(Long id, String nombre, String email, Role rol) {
        this.id = id;
        this.nombre = nombre;
        this.email = email;
        this.rol = rol;
    }

    public UserResponseDTO(Long id, String nombre, String email, Role rol, String token) {
        this.id = id;
        this.nombre = nombre;
        this.email = email;
        this.rol = rol;
        this.token = token;
    }

    public Long getId() {
        return id;
    }

    public String getNombre() {
        return nombre;
    }

    public String getEmail() {
        return email;
    }

    public Role getRol() {
        return rol;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }
}