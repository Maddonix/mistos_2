import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OnionsComponent } from './onions.component';

describe('OnionsComponent', () => {
  let component: OnionsComponent;
  let fixture: ComponentFixture<OnionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OnionsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(OnionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
