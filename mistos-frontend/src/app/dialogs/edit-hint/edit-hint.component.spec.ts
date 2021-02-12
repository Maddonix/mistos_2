import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditHintComponent } from './edit-hint.component';

describe('EditHintComponent', () => {
  let component: EditHintComponent;
  let fixture: ComponentFixture<EditHintComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditHintComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EditHintComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
