import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { Classifier } from 'src/app/models/classifier.model';
import { ClassifierService } from 'src/app/shared/classifier.service';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-classifier-hint',
  templateUrl: './classifier-hint.component.html',
  styleUrls: ['./classifier-hint.component.css']
})
export class ClassifierHintComponent implements OnInit {
  classifier: Classifier;
  subscription: Subscription;

  constructor(
    private classifierService: ClassifierService,
    private route: ActivatedRoute,
    private router: Router,
    private comService: ComService,
  ) { }

  ngOnInit() {
    this.route.data.subscribe((data:Data) => {
      this.classifier = data["classifier"];
    });
  }

  onPrint() {
    console.log(this.classifier);
  }
}
