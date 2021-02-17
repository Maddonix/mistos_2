import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { EditChannelsComponent } from 'src/app/dialogs/edit-channels/edit-channels.component';
import { EditHintComponent } from 'src/app/dialogs/edit-hint/edit-hint.component';
import { EditNameComponent } from 'src/app/dialogs/edit-name/edit-name.component';
import { ImageResultLayer } from 'src/app/models/image-result-layer.model';
import { Image } from 'src/app/models/image.model';
import { ComService } from 'src/app/shared/com.service';
import { ImageService } from 'src/app/shared/image.service';

@Component({
  selector: 'app-image-detail',
  templateUrl: './image-detail.component.html',
  styleUrls: ['./image-detail.component.css']
})
export class ImageDetailComponent implements OnInit {
  image: Image;
  metadata: {};
  // Define Dialog Configuration
  dialogConfig = new MatDialogConfig();
  thumbnailPath:string;
  

  constructor(
    private imageService: ImageService,
    private route: ActivatedRoute,
    private router: Router,
    private comService: ComService,
    private dialog: MatDialog
  ) { }

  ngOnInit() {
    this.route.data.subscribe((data:Data) => {
      this.image = data["image"];
    });
    console.log(this.image);
    this.metadata = this.image.metadata;

    //fetch Thumbnail Path
    this.comService.fetchImageThumbnailPath(this.image.uid).subscribe((path:string)=>{
      this.thumbnailPath = path["path"];
    });

    //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
    this.dialogConfig.data = {
      hint: this.image.hint,
      channels: this.metadata["custom_channel_names"]
    };
  }

  filterMeasurements(layerId) {
    return this.image.measurements.filter(m => m.resultLayerId === layerId);
  }

  onOpenInViewer() {
    this.comService.viewImage(
      this.image.uid,
      true, true
    )
  }

  onEditChannels() {
    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditChannelsComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newChannels:[])=> {
      if (typeof newChannels === typeof []) {
        this.comService.updateImageChannelNames(this.image.uid, newChannels["channels"]).subscribe(response=>{
          this.comService.fetchImageById(this.image.uid).subscribe((image:Image)=>{
            this.image = image;
            this.metadata = this.image.metadata;
          })
        });
      } else {
        console.log("Edit Image Channel names was aborted.");
      }
    }
  );  
  }

  onEditHint() {
    this.dialogConfig.data = {
      hint: this.image.hint,
      channels: this.metadata["custom_channel_names"]
    };
    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditHintComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newHint:string)=> {
      if (typeof newHint === typeof "") {
        this.comService.updateImageHint(this.image.uid, newHint).subscribe(response => {
          this.comService.fetchImageById(this.image.uid).subscribe((image:Image)=>{
            this.image = image;
          });
        }
        );
      } else {
        console.log("Edit Image Hint was aborted.");
      }
    }
    )
  }

  onEditLayerName(layer:ImageResultLayer) {
    this.dialogConfig.data = {
      name: layer.name
    };
    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditNameComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newName:string)=> {
      if (typeof newName === typeof "") {
        this.comService.updateLayerName(layer.uid, newName).subscribe(response => {
          this.comService.fetchImageById(this.image.uid).subscribe((image:Image)=>{
            this.image = image;
          });
        }
        );
      } else {
        console.log("Edit Description was aborted.");
      }
    }
    )
  }

  onExportMistosImage(){
    this.comService.exportMistosImage(this.image.uid).subscribe()
  }

  onDeleteLayer(layerId:number){
    this.comService.deleteResultLayer(layerId).subscribe(response => {
      this.comService.fetchImageById(this.image.uid).subscribe((image:Image)=>{
        this.image = image;
      });
    });
  }

  onEditLayerHint(layer:ImageResultLayer) {
    this.dialogConfig.data = {
      hint: layer.hint
    };
    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      EditHintComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((newHint:string)=> {
      if (typeof newHint === typeof "") {
        this.comService.updateLayerHint(layer.uid, newHint).subscribe(response => {
          this.comService.fetchImageById(this.image.uid).subscribe((image:Image)=>{
            this.image = image;
          });
        }
        );
      } else {
        console.log("Edit Hint was aborted.");
      }
    }
    )
  }
  

}
