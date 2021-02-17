import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { Experiment } from 'src/app/models/experiment.model';
import { ComService } from 'src/app/shared/com.service';
import { ExperimentService } from 'src/app/shared/experiment.service';

@Component({
  selector: 'app-experiment-hint',
  templateUrl: './experiment-hint.component.html',
  styleUrls: ['./experiment-hint.component.css']
})
export class ExperimentHintComponent implements OnInit {
  experiment: Experiment;
  subscription: Subscription;

  constructor(
    private experimentService: ExperimentService,
    private route: ActivatedRoute,
    private router: Router,
    private comService: ComService,
  ) { }

  ngOnInit(): void {
    // Subscribe to active experiment
    // this.subscription = this.experimentService.activeExperiment.subscribe((experiment:Experiment) => {
    //   this.experiment = experiment;
    // });
    this.route.data.subscribe((data:Data) => {
      this.experiment = data["experiment"];
    });
  }
    
  onPrint() {
    console.log(this.experiment);
  }

}
