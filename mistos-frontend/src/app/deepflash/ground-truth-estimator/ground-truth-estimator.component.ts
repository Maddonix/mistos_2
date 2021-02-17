import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { AddImageToGroupComponent } from 'src/app/dialogs/add-image-to-group/add-image-to-group.component';
import { ImageResultLayer } from 'src/app/models/image-result-layer.model';
import { Image } from 'src/app/models/image.model';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-ground-truth-estimator',
  templateUrl: './ground-truth-estimator.component.html',
  styleUrls: ['./ground-truth-estimator.component.css']
})
export class GroundTruthEstimatorComponent implements OnInit {
  truthImageList: Image[] = [];
  imageList: Image[] = [];
  optionsForm: FormGroup;
  layersForm: FormGroup;
  dialogConfig = new MatDialogConfig();
  numberExperts: number = 0;
  rangeExperts = [];
  layerChoices = {};
  thumbnailPaths:string[]=[];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private comService: ComService,
    private dialog: MatDialog,
    private formBuilder: FormBuilder
    ) { }

  ngOnInit(): void {
    this.route.data.subscribe((data:Data) => {
      this.imageList = data["imageList"];
      this.optionsForm = this.formBuilder.group({
        "model": new FormControl(null, Validators.required)
      });
    });
    this.layersForm = this.formBuilder.group({});

    //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
  }
  

  addControls(imageId, imageControls) {
    for (let i of this.range(this.numberExperts)) {
      let key = imageId.toString() + "_" + i.toString();
      imageControls[key] = new FormControl(null, Validators.required);
    }
    return imageControls;
  }

  createChoices(image:Image){
    let choices = [];
    for (let layer of image.imageResultLayers) {
      choices.push({
        layerId: layer.uid, viewValue: layer.name
      })
    };
    return choices
  }

  onCreateNewForm(){
    this.rangeExperts = this.range(this.numberExperts);
    let imageControls = {};
    this.layerChoices = {};
    for (let image of this.truthImageList) {
      imageControls = this.addControls(image.uid, imageControls);
      this.layerChoices[image.uid] = this.createChoices(image);
    };
    console.log(imageControls);
    this.layersForm = new FormGroup(imageControls);
    
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
            this.truthImageList.push(image);
          });
          this.comService.fetchImageThumbnailPath(imageId).subscribe((path:string)=>{
            this.thumbnailPaths.push(path["path"]);
          });
        }
      } else {
        console.log("Add Images was aborted.");
      }
    }
    )
  }

  onDeleteImageFromList(index:number) {
    this.truthImageList.splice(index, 1);
    this.thumbnailPaths.splice(index, 1);
  }

  onCalculateGroundTruth() {
    // KEYS FOR RESULT ARE: "{image_id}_{n_expert}"
    console.log(this.layersForm.value);
    this.comService.estimateGroundTruth(this.layersForm.value).subscribe();
  }

  range(start, stop?, step?) {
    if (typeof stop == 'undefined') {
        // one param defined
        stop = start;
        start = 0;
    }

    if (typeof step == 'undefined') {
        step = 1;
    }

    if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
        return [];
    }

    var result = [];
    for (var i = start; step > 0 ? i < stop : i > stop; i += step) {
        result.push(i);
    }

    return result;
};

}
