'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTaskStore } from '@/store/tasks';
import { useAuthStore } from '@/store/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Progress } from '@/components/ui/progress';

const taskSchema = z.object({
  image: z.instanceof(File),
  metadata: z.string().optional(),
});

type TaskForm = z.infer<typeof taskSchema>;

export default function DashboardPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<TaskForm>({
    resolver: zodResolver(taskSchema),
  });
  const [uploading, setUploading] = useState(false);
  const { tasks, loading, error, fetchTasks, createTask } = useTaskStore();
  const { user } = useAuthStore();
  const { toast } = useToast();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const onSubmit = async (data: TaskForm) => {
    if (!user || user.credits < 1) {
      toast({
        title: 'Error',
        description: 'Not enough credits to process image',
        variant: 'destructive',
      });
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('image', data.image);
    if (data.metadata) {
      formData.append('metadata', data.metadata);
    }

    try {
      await createTask(formData);
      toast({
        title: 'Success',
        description: 'Image uploaded successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to upload image',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Upload Image</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="image">Image</Label>
                  <Input
                    id="image"
                    type="file"
                    accept="image/*"
                    {...register('image')}
                  />
                  {errors.image && (
                    <p className="text-sm text-red-500">{errors.image.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="metadata">Metadata (Optional)</Label>
                  <Input
                    id="metadata"
                    {...register('metadata')}
                    placeholder="Enter metadata"
                  />
                </div>
                <Button type="submit" className="w-full" disabled={uploading}>
                  {uploading ? 'Uploading...' : 'Upload Image'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Task List</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <Progress value={100} className="animate-pulse" />
              ) : error ? (
                <p className="text-red-500">{error}</p>
              ) : (
                <div className="space-y-4">
                  {tasks.map((task) => (
                    <Card key={task.id}>
                      <CardContent className="p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-medium">Task #{task.id}</p>
                            <p className="text-sm text-gray-500">
                              Status: {task.status}
                            </p>
                          </div>
                          {task.result_path && (
                            <Button
                              variant="outline"
                              onClick={() => window.open(`/uploads/${task.result_path}`, '_blank')}
                            >
                              View Result
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 