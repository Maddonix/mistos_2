import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { MatTableFilter } from 'mat-table-filter';
import { Subscription } from 'rxjs';
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


  constructor(
    private comService: ComService,
    private imageService: ImageService,
    private route: ActivatedRoute,
    private router: Router
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
  
  onPrint() {
    console.log(this.imageList);
    console.log(this.dataSource);
  }

  onView(imageId) {
    this.comService.viewImage(imageId, true, true);
  }

  onSelect(imageId: number) {
    this.router.navigate([imageId, "hint"], {relativeTo: this.route});
  }

  onDelete(imageId: number) {
    this.comService.deleteImageById(imageId).subscribe((response) => {
      console.log("DeleteImageRequest:");
      console.log(response);
      
      this.comService.fetchImageList().subscribe((imageList:Image[]) => {
        this.imageList = imageList;
        this.onFetchData();
      });
  });
  }
}


