import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialog, MatDialogConfig, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Experiment } from 'src/app/models/experiment.model';

@Component({
  selector: 'app-experiment-create-new-dialog',
  templateUrl: './experiment-create-new-dialog.component.html',
  styleUrls: ['./experiment-create-new-dialog.component.css']
})
export class ExperimentCreateNewDialogComponent implements OnInit {

  form: FormGroup;

  constructor(
  private dialogRef: MatDialogRef<ExperimentCreateNewDialogComponent>
    // @Inject(MAT_DIALOG_DATA) public data: any //like this we could inject data into our dialog
  ) {}


    
  ngOnInit(): void {
    this.form = new FormGroup({
      "name": new FormControl("", Validators.required),
      "tags": new FormControl(""),
      "hint": new FormControl(""),
      "description": new FormControl("")
    })
    this.form.enable();
  }

  onSubmit() {
    // let tags = this.form.value.tags.split(";")
    let newExperiment = new Experiment()
    newExperiment.uid = -1;
    newExperiment.name = this.form.value.name;
    newExperiment.hint = this.form.value.hint;
    newExperiment.description = this.form.value.description;
    newExperiment.experimentGroups = [];
    newExperiment.tags = this.form.value.tags.split(";");
    this.dialogRef.close(newExperiment);
  }

  onClose() {
    this.dialogRef.close(false);
  }
   
}
