import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddImageToGroupComponent } from './add-image-to-group.component';

describe('AddImageToGroupComponent', () => {
  let component: AddImageToGroupComponent;
  let fixture: ComponentFixture<AddImageToGroupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddImageToGroupComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AddImageToGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
