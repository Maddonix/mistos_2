import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { MatTableFilter } from 'mat-table-filter';
import { Subscription } from 'rxjs';
import { WarningDeleteComponent } from 'src/app/dialogs/warning-delete/warning-delete.component';
import { Image } from 'src/app/models/image.model';
import { ComService } from 'src/app/shared/com.service';
import { ImageService } from 'src/app/shared/image.service';

@Component({
  selector: 'app-images-list',
  templateUrl: './images-list.component.html',
  styleUrls: ['./images-list.component.css']
})
export class ImagesListComponent implements AfterViewInit, OnInit {
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  filterEntity: Image;
  filterType: MatTableFilter;
  dataSource: MatTableDataSource<Image>;//ImagesListDataSource;
  imageList: Image[];
  subscription: Subscription;
  displayedColumns = ['uid', 'name', "tags", "actions"];
  dialogConfig = new MatDialogConfig();

  constructor(
    private comService: ComService,
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog
  ) {

  }

  ngOnInit() {
    this.route.data.subscribe((data:Data) => {
      this.imageList = data["imageList"];
    });
    // Components for filtering
    this.filterEntity = new Image();
    this.filterType = MatTableFilter.ANYWHERE;
    //create dataSource for table
    this.dataSource = new MatTableDataSource(this.imageList);

    //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
  }

  ngAfterViewInit() {
    // Here we define sorting, pagination and our datasource
    this.dataSource = new MatTableDataSource(this.imageList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  onFetchData() {
    this.dataSource = new MatTableDataSource(this.imageList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }
  
  onView(imageId) {
    this.comService.viewImage(imageId, true, true);
  }

  onSelect(imageId: number) {
    this.router.navigate([imageId, "hint"], {relativeTo: this.route});
  }

  onDelete(imageId: number) {
    this.dialogConfig.data = {
      warningInput: "this image"
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      WarningDeleteComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((proceed:boolean)=> {
      if (proceed === true) {
        this.comService.deleteImageById(imageId).subscribe((response) => {
          console.log("DeleteImageRequest:");
          console.log(response);
          
          this.comService.fetchImageList().subscribe((imageList:Image[]) => {
            this.imageList = imageList;
            this.onFetchData();
          });
      });
      } else {
        console.log("Delete Image was aboirted.");
      }
    }
    ) 
  }
}


