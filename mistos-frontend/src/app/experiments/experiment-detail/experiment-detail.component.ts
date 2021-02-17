import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { AddImageToGroupComponent } from 'src/app/dialogs/add-image-to-group/add-image-to-group.component';
import { EditDescriptionComponent } from 'src/app/dialogs/edit-description/edit-description.component';
import { EditHintComponent } from 'src/app/dialogs/edit-hint/edit-hint.component';
import { EditNameComponent } from 'src/app/dialogs/edit-name/edit-name.component';
import { ExportExperimentComponent } from 'src/app/dialogs/export-experiment/export-experiment.component';
import { WarningDeleteComponent } from 'src/app/dialogs/warning-delete/warning-delete.component';
import { ExperimentGroup } from 'src/app/models/experiment-group.model';
import { Experiment } from 'src/app/models/experiment.model';
import { ImageResultLayer } from 'src/app/models/image-result-layer.model';
import { Image } from 'src/app/models/image.model';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-experiment-detail',
  templateUrl: './experiment-detail.component.html',
  styleUrls: ['./experiment-detail.component.css']
})
export class ExperimentDetailComponent implements OnInit {
  experiment: Experiment;
  imageList: Image[];
  metadata: {};
  // Define Dialog Configuration
  dialogConfig = new MatDialogConfig();
  

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private comService: ComService,
    private dialog: MatDialog
  ) { }

  ngOnInit() {
    this.route.data.subscribe((data:Data) => {
      this.experiment = data["experiment"];
      this.imageList = data["imageList"];
    });
    console.log(this.experiment);
    console.log(this.imageList);

    //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
  }

  onCalculateResults() {
    this.comService.calculateExperimentResults(this.experiment.uid).subscribe(response => {
      this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
        this.experiment=experiment;
      });
    });
  }

  onAddGroup() {
    this.comService.newExperimentGroup(this.experiment.uid).subscribe(response => {
      this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
        this.experiment=experiment;
      });
    });
  };

  onDeleteExperiment() {
    this.dialogConfig.data = {
      warningInput: "this experiment"
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      WarningDeleteComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((proceed:boolean)=> {
      if (proceed === true) {
        this.comService.deleteExperiment(this.experiment.uid).subscribe(response => {
          this.router.navigate(["../../"], {relativeTo: this.route})
        });
      } else {
        console.log("Delete experiment was aboirted.");
      }
    }
    ) 



    
  }

  onDeleteGroup(groupId) {
    this.comService.deleteExperimentGroup(this.experiment.uid, groupId).subscribe(response => {
      this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
        this.experiment=experiment;
      });
    });
  };

  onEditName() {
    this.dialogConfig.data = {
      hint: this.experiment.hint,
      description: this.experiment.description,
      name: this.experiment.name
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditNameComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newName:string)=> {
      console.log(newName);
      if (typeof newName === typeof "") {
        this.comService.updateExperimentName(this.experiment.uid, newName).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
          });
        }
        );
      } else {
        console.log("Edit Description was aborted.");
      }
    }
    )
  }

  onEditHint() {
    this.dialogConfig.data = {
      hint: this.experiment.hint,
      description: this.experiment.description
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditHintComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newHint:string)=> {
      if (typeof newHint === typeof "") {
        this.comService.updateExperimentHint(this.experiment.uid, newHint).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
          });
        }
        );
      } else {
        console.log("Edit Experiment Hint was aborted.");
      }
    }
    )
  }

  onEditDescription() {
    this.dialogConfig.data = {
      hint: this.experiment.hint,
      description: this.experiment.description
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditDescriptionComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newDescription:string)=> {
      console.log(newDescription);
      if (typeof newDescription === typeof "") {
        this.comService.updateExperimentDescription(this.experiment.uid, newDescription).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
          });
        }
        );
      } else {
        console.log("Edit Description was aborted.");
      }
    }
    )
  }

  onAddImage(group) {
    this.dialogConfig.data = {
      imageList: this.imageList
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      AddImageToGroupComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((imageIdList:number[])=> {
      if (typeof imageIdList === typeof [2,3]) {
        this.comService.updateExperimentGroupImages(group.uid, imageIdList).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
            console.log(this.experiment);
          });
        }
        );
      } else {
        console.log("Edit Images was aborted.");
      }
    }
    )
  }

  onViewImage(image) {
    this.comService.viewImage(image.uid, true, true);
  }

  onImageDetail(image) {
    this.router.navigate(["images", image.uid.toString(), "detail"]);
  }

  sortById(list:Image[]) {
    return list.sort((a,b)=>(a.uid > b.uid) ? 1:-1);
  }

  getActiveLayer(group: ExperimentGroup, image:Image) {
    let activeLayer: ImageResultLayer;
    let imageLayerIds = [];
    for (let layer of image.imageResultLayers) {
      imageLayerIds.push(layer.uid);
    }
    for (let layerId of group.resultLayerIds) {
      let index = imageLayerIds.indexOf(layerId);
      if (index > -1) {
        activeLayer = image.imageResultLayers[index];
      }
    }
    // Iterate over list of active Image Layers in this group
    // if the result layers image id matches images' id, return
    return activeLayer
  }

  getActiveLayerName(group:ExperimentGroup, image:Image) {
    let layer = this.getActiveLayer(group, image);
    if (typeof(layer) != "undefined"){
      return layer.name;
    }
    else {
      return "None";
    }
    
  }

  addResultLayerToGroup(groupId, layerId) {
    // Currently only 1 Layer per image may be active, if a new one is set, the old one gets removed from the list in backend
    this.comService.addResultLayertoGroup(groupId, layerId).subscribe(response => {
      this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
        this.experiment=experiment;
      });
    });
  }

  onRemoveImageFromGroup(groupId, imageId) {
    this.comService.deleteImageFromExperimentGroup(groupId, imageId).subscribe(response => {
      this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
        this.experiment=experiment;
      });
    });
  }

  onEditGroupName(group) {
    this.dialogConfig.data = {
      hint: group.hint,
      description: group.description,
      name: group.name
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditNameComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newName:string)=> {
      console.log(newName);
      if (typeof newName === typeof "") {
        this.comService.updateExperimentGroupName(group.uid, newName).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
          });
        }
        );
      } else {
        console.log("Edit Description was aborted.");
      }
    }
    )
  }

  onEditGroupHint(group) {
    this.dialogConfig.data = {
      hint: group.hint,
      description: group.description
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditHintComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newHint:string)=> {
      if (typeof newHint === typeof "") {
        this.comService.updateExperimentGroupHint(group.uid, newHint).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
          });
        }
        );
      } else {
        console.log("Edit Hint was aborted.");
      }
    }
    )
  }
  
  onEditGroupDescription(group){
    this.dialogConfig.data = {
      hint: group.hint,
      description: group.description
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditDescriptionComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newDescription:string)=> {
      console.log(newDescription);
      if (typeof newDescription === typeof "") {
        this.comService.updateExperimentGroupDescription(group.uid, newDescription).subscribe(response => {
          this.comService.fetchExperimentById(this.experiment.uid).subscribe((experiment:Experiment)=>{
            this.experiment = experiment;
          });
        }
        );
      } else {
        console.log("Edit Experiment Description was aborted.");
      }
    }
    )
  }

  onExportExperiment() {
    this.dialogConfig.data = {
      experimentId: this.experiment.uid
    };
    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      ExportExperimentComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((exportRequest)=> {
      console.log(exportRequest);
      if (typeof exportRequest === typeof {}) {
        this.comService.exportExperiment(this.experiment.uid, exportRequest).subscribe();
      } else {
        console.log("Edit Experiment Description was aborted.");
      }
    }
    )
  }

  onExportMistosExperiment() {
    this.comService.exportMistosExperiment(this.experiment.uid).subscribe();
  }

}
