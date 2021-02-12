import { Component, OnInit } from '@angular/core';
import { ComService } from './shared/com.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'mistos-frontend';

  constructor(private comService:ComService) {}

  ngOnInit() {
  }
}
