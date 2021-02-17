import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeepflashComponent } from './deepflash.component';

describe('DeepflashComponent', () => {
  let component: DeepflashComponent;
  let fixture: ComponentFixture<DeepflashComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeepflashComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DeepflashComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
