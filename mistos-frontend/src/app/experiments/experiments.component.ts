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
    public dialog: MatDialog,
    private comService:ComService,
    private router:Router,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
  }

  onCreateNewExperiment() {
    // Define Dialog Configuration
    let dialogConfig = new MatDialogConfig();
    dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      ExperimentCreateNewDialogComponent,
      dialogConfig
    );
    dialogRef.afterClosed().subscribe((newExperiment:Experiment)=> {
      if (newExperiment instanceof Experiment) {
        this.comService.createNewExperiment(newExperiment).subscribe((response) => {});
      } else {
        console.log("aborted");
      }
      
    }
  );  
  }

}
