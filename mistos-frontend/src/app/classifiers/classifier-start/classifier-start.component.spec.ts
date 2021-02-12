import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassifierStartComponent } from './classifier-start.component';

describe('ClassifierStartComponent', () => {
  let component: ClassifierStartComponent;
  let fixture: ComponentFixture<ClassifierStartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClassifierStartComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassifierStartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
