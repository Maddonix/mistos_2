import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClassifierHintComponent } from './classifier-hint.component';

describe('ClassifierHintComponent', () => {
  let component: ClassifierHintComponent;
  let fixture: ComponentFixture<ClassifierHintComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClassifierHintComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ClassifierHintComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
