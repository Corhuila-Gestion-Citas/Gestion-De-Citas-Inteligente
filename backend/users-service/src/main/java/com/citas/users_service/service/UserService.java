package com.citas.users_service.service;

import com.citas.users_service.dto.UserRequestDTO;
import com.citas.users_service.dto.UserResponseDTO;
import com.citas.users_service.model.Role;
import com.citas.users_service.model.User;
import com.citas.users_service.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public UserResponseDTO create(UserRequestDTO request) {

        String email = request.getEmail().trim().toLowerCase();
        String password = request.getPassword().trim();

        if (userRepository.existsByEmail(email)) {
            throw new RuntimeException("Ya existe un usuario con ese correo");
        }

        User user = new User();
        user.setNombre(request.getNombre().trim());
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(password));
        user.setRol(Role.CLIENTE);

        User saved = userRepository.save(user);

        return new UserResponseDTO(
                saved.getId(),
                saved.getNombre(),
                saved.getEmail(),
                saved.getRol()
        );
    }

    public List<UserResponseDTO> findAll() {
        return userRepository.findAll()
                .stream()
                .map(user -> new UserResponseDTO(
                        user.getId(),
                        user.getNombre(),
                        user.getEmail(),
                        user.getRol()))
                .toList();
    }

    public UserResponseDTO findById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        return new UserResponseDTO(
                user.getId(),
                user.getNombre(),
                user.getEmail(),
                user.getRol()
        );
    }

    public UserResponseDTO update(Long id, UserRequestDTO request) {

        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        String email = request.getEmail().trim().toLowerCase();

        if (!user.getEmail().equals(email) && userRepository.existsByEmail(email)) {
            throw new RuntimeException("Ya existe un usuario con ese correo");
        }

        user.setNombre(request.getNombre().trim());
        user.setEmail(email);

        if (request.getPassword() != null && !request.getPassword().isBlank()) {
            user.setPassword(passwordEncoder.encode(request.getPassword().trim()));
        }

        user.setRol(user.getRol());

        User updated = userRepository.save(user);

        return new UserResponseDTO(
                updated.getId(),
                updated.getNombre(),
                updated.getEmail(),
                updated.getRol()
        );
    }

    public void delete(Long id) {
        if (!userRepository.existsById(id)) {
            throw new RuntimeException("Usuario no encontrado");
        }

        userRepository.deleteById(id);
    }

    public UserResponseDTO login(String email, String password) {

        String cleanEmail = email.trim().toLowerCase();
        String cleanPassword = password.trim();

        User user = userRepository.findByEmail(cleanEmail)
                .orElseThrow(() -> new RuntimeException("Credenciales inválidas"));

        if (!passwordEncoder.matches(cleanPassword, user.getPassword())) {
            throw new RuntimeException("Credenciales inválidas");
        }

        String token = jwtService.generateToken(user);
        UserResponseDTO response = new UserResponseDTO(
                user.getId(),
                user.getNombre(),
                user.getEmail(),
                user.getRol(),
                token
        );

        return response;
    }

    public boolean canAccessUser(Long currentUserId, Long requestedUserId, Role currentRole) {
        return currentRole == Role.ADMIN || currentUserId != null && currentUserId.equals(requestedUserId);
    }
}