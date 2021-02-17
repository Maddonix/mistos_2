import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeepflashModelsComponent } from './deepflash-models.component';

describe('DeepflashModelsComponent', () => {
  let component: DeepflashModelsComponent;
  let fixture: ComponentFixture<DeepflashModelsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeepflashModelsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DeepflashModelsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
