import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageStartComponent } from './image-start.component';

describe('ImageStartComponent', () => {
  let component: ImageStartComponent;
  let fixture: ComponentFixture<ImageStartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ImageStartComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ImageStartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
