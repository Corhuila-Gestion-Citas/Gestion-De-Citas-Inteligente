import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { TurnoStoreService } from '../../services/turno-store';
import { UsuarioService } from '../../services/usuario.service';
import { Inicio } from './inicio';

describe('Inicio', () => {
  let component: Inicio;
  let fixture: ComponentFixture<Inicio>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Inicio],
      providers: [
        provideRouter([]),
        {
          provide: UsuarioService,
          useValue: {
            obtenerSesion: () => ({ id: 1, nombre: 'Paciente', email: 'paciente@example.com', rol: 'CLIENTE' })
          }
        },
        { provide: TurnoStoreService, useValue: { obtenerTurnos: () => of([]) } }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Inicio);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('creates the dashboard for an authenticated user', () => {
    expect(component).toBeTruthy();
    expect(component.usuario?.id).toBe(1);
  });
});
