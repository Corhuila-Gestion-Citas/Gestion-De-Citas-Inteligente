import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { NotificacionesService } from './notificaciones';

describe('NotificacionesService', () => {
  it('is created', () => {
    TestBed.configureTestingModule({ providers: [provideHttpClient()] });
    expect(TestBed.inject(NotificacionesService)).toBeTruthy();
  });
});
