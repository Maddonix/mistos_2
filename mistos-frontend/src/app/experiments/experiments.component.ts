import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { cpuUsage } from 'process';
import { Experiment } from '../models/experiment.model';
import { ComService } from '../shared/com.service';
import { ExperimentCreateNewDialogComponent } from '../dialogs/experiment-create-new-dialog/experiment-create-new-dialog.component';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-experiments',
  templateUrl: './experiments.component.html',
  styleUrls: ['./experiments.component.css']
})
export class ExperimentsComponent implements OnInit {

  constructor(
  ) { }

  ngOnInit(): void {
  }

  

}
