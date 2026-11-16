import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuditService } from '../../services/audit.service';
import { NotificacionesService } from '../../services/notificaciones';
import { TurnoStoreService } from '../../services/turno-store';
import { UsuarioService } from '../../services/usuario.service';

import { MisTurnos } from './mis-turnos';

describe('MisTurnos', () => {
  let component: MisTurnos;
  let fixture: ComponentFixture<MisTurnos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MisTurnos],
      providers: [
        provideRouter([]),
        { provide: UsuarioService, useValue: { obtenerSesion: () => ({ id: 1 }) } },
        { provide: TurnoStoreService, useValue: { obtenerTurnos: () => of([]) } },
        { provide: NotificacionesService, useValue: {} },
        { provide: AuditService, useValue: {} }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MisTurnos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
