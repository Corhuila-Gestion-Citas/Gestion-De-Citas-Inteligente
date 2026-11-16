import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { API_GATEWAY_URL } from '../config/api.config';
import { UsuarioService } from './usuario.service';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const usuarioService = inject(UsuarioService);
  const router = inject(Router);
  const apiBaseUrl = new URL(API_GATEWAY_URL);
  const requestUrl = new URL(request.url, apiBaseUrl);
  const apiBasePath = apiBaseUrl.pathname.replace(/\/+$/, '');
  const isApiRequest = requestUrl.origin === apiBaseUrl.origin
    && (!apiBasePath || requestUrl.pathname === apiBasePath || requestUrl.pathname.startsWith(`${apiBasePath}/`));
  const isLoginRequest = requestUrl.pathname.endsWith('/users/login');
  const token = isApiRequest && !isLoginRequest ? usuarioService.obtenerToken() : null;
  const authenticatedRequest = token
    ? request.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : request;

  return next(authenticatedRequest).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status === 401 && token) {
        usuarioService.cerrarSesion();
        void router.navigate(['/login']);
      }
      return throwError(() => error);
    })
  );
};
