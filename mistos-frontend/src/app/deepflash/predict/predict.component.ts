import { Component, OnInit, ɵAPP_ID_RANDOM_PROVIDER } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { Image } from 'src/app/models/image.model';
import { ComService } from 'src/app/shared/com.service';
import { AddImageToGroupComponent } from 'src/app/dialogs/add-image-to-group/add-image-to-group.component';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Classifier } from 'src/app/models/classifier.model';

@Component({
  selector: 'app-predict',
  templateUrl: './predict.component.html',
  styleUrls: ['./predict.component.css']
})
export class PredictComponent implements OnInit {
  imageList: Image[];
  predictImageList: Image[] = [];
  metadata: {};
  models: Classifier[];
  optionsForm: FormGroup;
  // Define Dialog Configuration
  dialogConfig = new MatDialogConfig();

  /////////////////////////// TO DO: GET MODELS FROM BACKEND ///////////////////////////////////////

  constructor(
    private route: ActivatedRoute,
    private comService: ComService,
    private dialog: MatDialog,
    private formBuilder: FormBuilder
    ) { }

  ngOnInit(): void {
    this.route.data.subscribe((data:Data) => {
      this.imageList = data["imageList"];
      this.models = data["dfClassifierList"];
      this.optionsForm = this.formBuilder.group({
        "model": new FormControl(null, Validators.required)
      });
    });

    //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
  }

  onAddImage(){
    this.dialogConfig.data = {
      imageList: this.imageList
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      AddImageToGroupComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((imageIdList:number[])=> {
      console.log(imageIdList);
      if (typeof imageIdList === typeof [2,3]) {
        for (let imageId of imageIdList) {
          this.comService.fetchImageById(imageId).subscribe((image:Image)=> {
            this.predictImageList.push(image);
            console.log(this.predictImageList);
          });
        }
      } else {
        console.log("Add Images was aborted.");
      }
    }
    )
  }

  onDeleteImageFromList(index:number) {
    this.predictImageList.splice(index, 1);
  }

  onPredict() {
    console.log(this.optionsForm.value.model);
    console.log(this.predictImageList);
    let idList = [];
    for (let image of this.predictImageList) {
      idList.push(image.uid);
    };
    this.comService.deepflashPredictImages(
      this.optionsForm.value.model,
      idList,
    ).subscribe()
  }

}
