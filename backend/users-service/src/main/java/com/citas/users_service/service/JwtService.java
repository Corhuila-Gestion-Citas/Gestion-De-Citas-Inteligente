package com.citas.users_service.service;

import com.citas.users_service.model.Role;
import com.citas.users_service.model.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.security.KeyFactory;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import java.util.Date;

@Service
public class JwtService {

    @Value("${jwt.private-key-base64}")
    private String privateKeyBase64;

    @Value("${jwt.public-key-base64}")
    private String publicKeyBase64;

    @Value("${jwt.expiration-ms:900000}")
    private long jwtExpirationMs;

    public String generateToken(User user) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtExpirationMs);

        return Jwts.builder()
                .setIssuer("gestion-citas")
                .setSubject(user.getEmail())
                .claim("userId", user.getId())
                .claim("role", user.getRol().name())
                .setIssuedAt(now)
                .setExpiration(expiry)
                .signWith(getSigningKey(), SignatureAlgorithm.RS256)
                .compact();
    }

    public boolean isValidToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(getVerificationKey())
                    .requireIssuer("gestion-citas")
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (Exception ex) {
            return false;
        }
    }

    public Claims extractClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getVerificationKey())
                .requireIssuer("gestion-citas")
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    public String extractEmail(String token) {
        return extractClaims(token).getSubject();
    }

    public Long extractUserId(String token) {
        return extractClaims(token).get("userId", Long.class);
    }

    public Role extractRole(String token) {
        String roleName = extractClaims(token).get("role", String.class);
        return roleName == null ? null : Role.valueOf(roleName);
    }

    private RSAPrivateKey getSigningKey() {
        try {
            byte[] keyBytes = Base64.getDecoder().decode(privateKeyBase64);
            RSAPrivateKey key = (RSAPrivateKey) KeyFactory.getInstance("RSA")
                    .generatePrivate(new PKCS8EncodedKeySpec(keyBytes));
            if (key.getModulus().bitLength() < 2048) {
                throw new IllegalStateException("RSA signing key must be at least 2048 bits");
            }
            return key;
        } catch (Exception ex) {
            throw new IllegalStateException("JWT_PRIVATE_KEY_BASE64 must contain a valid PKCS#8 RSA private key", ex);
        }
    }

    private RSAPublicKey getVerificationKey() {
        try {
            byte[] keyBytes = Base64.getDecoder().decode(publicKeyBase64);
            RSAPublicKey key = (RSAPublicKey) KeyFactory.getInstance("RSA")
                    .generatePublic(new X509EncodedKeySpec(keyBytes));
            if (key.getModulus().bitLength() < 2048) {
                throw new IllegalStateException("RSA verification key must be at least 2048 bits");
            }
            return key;
        } catch (Exception ex) {
            throw new IllegalStateException("JWT_PUBLIC_KEY_BASE64 must contain a valid X.509 RSA public key", ex);
        }
    }
}
