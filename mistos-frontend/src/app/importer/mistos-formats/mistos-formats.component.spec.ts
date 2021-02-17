import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MistosFormatsComponent } from './mistos-formats.component';

describe('MistosFormatsComponent', () => {
  let component: MistosFormatsComponent;
  let fixture: ComponentFixture<MistosFormatsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MistosFormatsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MistosFormatsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
