import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { EditNameComponent } from 'src/app/dialogs/edit-name/edit-name.component';
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
  dialogConfig = new MatDialogConfig();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog,
    private comService: ComService
  ) { }

  ngOnInit() {
    this.route.data.subscribe((data:Data) => {
      this.classifier = data["classifier"];
    });

    //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
  }

  onRename() {
    this.dialogConfig.data = {
      name: this.classifier.name
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditNameComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newName:string)=> {
      console.log(newName);
      if (typeof newName === typeof "") {
        this.comService.updateClassifierName(this.classifier.uid, newName).subscribe();
      } else {
        console.log("Edit Name was aborted.");
      }
    }
    )
  }
}
